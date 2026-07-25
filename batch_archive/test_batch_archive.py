#!/usr/bin/env python3
"""Small regression check for recursive extraction and directory cleanup."""

import importlib.util
import sys
import tempfile
from unittest.mock import patch
from pathlib import Path


SPEC = importlib.util.spec_from_file_location(
    "batch_archive", Path(__file__).with_name("batch_archive.py"))
batch_archive = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(batch_archive)


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        current = Path(temporary)
        (current / "notouch.txt").write_text("keep.txt\n")
        with patch("pathlib.Path.cwd", return_value=current):
            assert batch_archive.no_touch_file(None) == current / "notouch.txt"
            explicit = current / "other.txt"
            assert batch_archive.no_touch_file(explicit) == explicit
        (current / "notouch.txt").unlink()
        with patch("pathlib.Path.cwd", return_value=current):
            assert batch_archive.no_touch_file(None) is None

        root = current / "input"
        root.mkdir()
        (root / "original.rom").touch()
        batch_archive.backup_input(root, False)
        assert (batch_archive.backup_path(root) / "original.rom").is_file()

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "roms"
        root.mkdir()
        assert batch_archive.output_path(root, None, "7z") == root.parent / "roms.7z"
        (root / "outer.lha").touch()
        extracted: list[str] = []

        batch_archive.ensure_command = lambda _: None

        def fake_run(command: list[str], cwd: Path, _test: bool, _input: str | None = None) -> None:
            if command[0] == "zip":
                return
            archive = Path(command[-1])
            extracted.append(archive.relative_to(root).as_posix())
            destination = (Path(command[-1]) if command[0] == "unzip"
                           else cwd if command[0] == "lha"
                           else Path(command[3][2:]))
            assert command[:2] == ["lha", "x"]
            if archive.name == "outer.lha":
                destination.mkdir(exist_ok=True)
                (destination / "inner.lha").touch()
                (destination / "game.rom").touch()

        batch_archive.run = fake_run
        expanded = batch_archive.expand_archives(root, [[], []], False)
        assert extracted == ["outer.lha", "outer-lha/inner.lha"]
        assert {path.relative_to(root).as_posix() for path in expanded} == set(extracted)

        batch_archive.create_archive(
            root, root.parent / "roms.zip", "zip", [[], []], expanded, True)
        batch_archive.delete_extracted(root, expanded, [[], []], False)
        assert not (root / "outer-lha").exists()
        assert (root / "outer.lha").exists()

        immediate = root / "immediate.rom"
        immediate.touch()
        added: list[Path] = []
        def removes_after_adding(command: list[str], cwd: Path, _test: bool, input_text: str | None = None) -> None:
            assert command[:2] == ["zip", "-q"]
            added.extend(root / name[2:] for name in command[3:])
        batch_archive.run = removes_after_adding
        batch_archive.create_archive(root, root.parent / "roms.zip", "zip", [[], []], set(), False)
        assert immediate in added
        assert immediate.exists()
        batch_archive.run = fake_run

        assert batch_archive.extract_destination(root / "outer.lha", True) == root / "outer-lha"
        assert batch_archive.extract_destination(root / "outer.lha", False) == root / "outer"
        with patch.object(sys, "argv", ["batch_archive.py", "roms", "--no-lha-tag"]):
            assert batch_archive.parse_args().no_lha_tag

        preserved = root / "preserved"
        preserved.mkdir()
        (preserved / "keep.rom").touch()
        assert batch_archive.protected(preserved / "keep.rom", root, [[], ["preserved/"]])
        batch_archive.delete_extracted(root, {root / "preserved.zip"}, [[], ["preserved/"]], False)
        assert (preserved / "keep.rom").exists()

        nested = root / "delete" / "me.txt"
        nested.parent.mkdir()
        nested.touch()
        protected = root / "keep.txt"
        protected.touch()
        files = [path for path in root.rglob("*")
                 if path.is_file()
                 and not batch_archive.protected(path, root, [[], ["keep.txt"]])]
        batch_archive.delete_archived(files, root, [[], ["keep.txt"]], False)
        assert not nested.parent.exists()
        assert protected.exists()

        temporary = root / "temporary"
        temporary.mkdir()
        temporary_file = temporary / "game.rom"
        temporary_file.touch()
        batch_archive.run = removes_after_adding
        batch_archive.create_archive(root, root.parent / "roms.zip", "zip", [[], []],
                                     {root / "temporary.zip"}, False)
        assert not temporary.exists()
        batch_archive.run = fake_run

        locked = root / "locked.zip"
        locked.touch()
        expanded = batch_archive.expand_archives(root, [[], ["locked.zip"]], False)
        assert locked not in expanded
        batch_archive.create_archive(
            root, root.parent / "roms.zip", "zip", [[], ["locked.zip"]], expanded, True)

        newline = root / "line\nbreak"
        newline.touch()
        assert batch_archive.unsafe_7z_path(root, set()) == newline

        batch_archive.create_archive(root, root.parent / "deleted.zip", "zip", [[], ["locked.zip"]],
                                     {locked}, False, delete=True)
        assert not root.exists()


if __name__ == "__main__":
    main()
