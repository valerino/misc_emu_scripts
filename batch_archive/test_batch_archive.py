#!/usr/bin/env python3
"""Small regression check for recursive extraction and directory cleanup."""

import contextlib
import importlib.util
import io
import subprocess
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
        (current / "keep.txt").write_text("keep.txt\n")
        with patch("pathlib.Path.cwd", return_value=current):
            assert batch_archive.keep_file(None) == current / "keep.txt"
            explicit = current / "other.txt"
            assert batch_archive.keep_file(explicit) == explicit
        (current / "keep.txt").unlink()
        with patch("pathlib.Path.cwd", return_value=current):
            assert batch_archive.keep_file(None) is None

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
        (root / "game.tar.gz").touch()
        extracted: list[str] = []

        batch_archive.ensure_command = lambda _: None

        def fake_run(command: list[str], cwd: Path, _test: bool, _input: str | None = None) -> None:
            if command[0] == "zip":
                return
            if command[0] == "tar":
                assert command[:2] == ["tar", "-xzf"]
                archive = Path(command[2])
                extracted.append(archive.relative_to(root).as_posix())
                (Path(command[-1]) / "game.rom").touch()
                return
            if command[0] == "lha":
                assert command[:2] == ["lha", "xf"]
                archive = Path(command[-1])
                extracted.append(archive.relative_to(root).as_posix())
                if archive.name == "outer.lha":
                    cwd.mkdir(exist_ok=True)
                    (cwd / "inner.lha").touch()
                    (cwd / "game.rom").touch()
                return
            assert command[:2] == ["7z", "x"]
            archive = Path(command[-1])
            extracted.append(archive.relative_to(root).as_posix())
            destination = Path(command[3][2:])

        batch_archive.run = fake_run
        expanded = batch_archive.expand_archives(root, [], [[], []], False)
        assert sorted(extracted) == ["game.tar.gz", "outer-lha/inner.lha", "outer.lha"]
        assert {path.relative_to(root).as_posix() for path in expanded} == {
            "outer-lha", "outer-lha/inner-lha", "game"}

        batch_archive.create_archive(
            root, root.parent / "roms.zip", "zip", [[], []], expanded, True)
        batch_archive.delete_extracted(root, expanded, [[], []], False)
        assert not (root / "outer-lha").exists()
        assert (root / "outer.lha").exists()

        immediate = root / "immediate.rom"
        immediate.touch()
        outer = root / "outer.lha"
        outer.touch()
        added: list[Path] = []
        def removes_after_adding(command: list[str], cwd: Path, _test: bool, input_text: str | None = None) -> None:
            assert command[:2] == ["zip", "-q"]
            added.extend(root / name[2:] for name in command[3:])
        batch_archive.run = removes_after_adding
        batch_archive.create_archive(root, root.parent / "roms.zip", "zip", [[], ["outer.lha"]],
                                     [root / "outer-lha"], False)
        assert immediate in added
        assert outer not in added
        assert immediate.exists()
        batch_archive.run = fake_run

        assert batch_archive.extract_destination(root / "outer.lha", True) == root / "outer-lha"
        assert batch_archive.extract_destination(root / "outer.lha", False) == root / "outer"
        with patch.object(sys, "argv", ["batch_archive.py", "roms", "--no-lha-tag"]):
            assert batch_archive.parse_args().no_lha_tag
        with patch.object(sys, "argv", ["batch_archive.py", "roms", "--no-recursive"]):
            assert batch_archive.parse_args().no_recursive

        preserved = root / "preserved"
        preserved.mkdir()
        (preserved / "keep.rom").touch()
        assert batch_archive.protected(preserved / "keep.rom", root, [[], ["preserved/"]])
        hidden = root / ".hidden"
        hidden.touch()
        assert not batch_archive.protected(hidden, root, [[], ["*"]])
        assert batch_archive.protected(hidden, root, [[]], keep_dotfiles=True)
        assert batch_archive.protected(root / "visible", root, [[], ["*"]])
        assert any(name == "./.hidden" for batch in
                   batch_archive.archive_batches(root, [], [[], ["*"]]) for _, name in batch)
        batch_archive.delete_extracted(root, [root / "preserved"], [[], ["preserved/"]], False)
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
                                     [root / "temporary"], False)
        assert not temporary.exists()
        batch_archive.run = fake_run

        locked = root / "locked.zip"
        locked.touch()
        expanded = batch_archive.expand_archives(root, [], [[], ["locked.zip"]], False)
        assert locked not in expanded
        batch_archive.create_archive(
            root, root.parent / "roms.zip", "zip", [[], ["locked.zip"]], expanded, True)

        newline = root / "line\nbreak"
        newline.touch()
        assert batch_archive.unsafe_7z_path(root, [], [[], []]) == newline

        batch_archive.create_archive(root, root.parent / "deleted.zip", "zip", [[], ["locked.zip"]],
                                     [], False, delete=True)
        assert root.exists()
        assert locked.exists()
        assert not (root / "line\nbreak").exists()

        batch_archive.create_archive(root, root.parent / "deleted.zip", "zip", [[], []],
                                     [], False, delete=True)
        assert not root.exists()

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "nested"
        root.mkdir()
        (root / "outer.lha").touch()
        extracted = []

        def fake_run(command: list[str], cwd: Path, _test: bool, _input: str | None = None) -> None:
            assert command[:2] == ["lha", "xf"]
            extracted.append(Path(command[-1]).relative_to(root).as_posix())
            cwd.mkdir(exist_ok=True)
            (cwd / "inner.lha").touch()

        batch_archive.run = fake_run
        expanded = batch_archive.expand_archives(root, [], [[]], False, recursive=False)
        assert extracted == ["outer.lha"]
        assert {path.relative_to(root).as_posix() for path in expanded} == {"outer-lha"}

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "fail"
        root.mkdir()
        output = root.parent / "fail.zip"

        def failing(*_args: object, **_kwargs: object) -> None:
            raise RuntimeError("boom")

        def run_main(create: object) -> tuple[str, bool]:
            stream = io.StringIO()
            exited = False
            arguments = ["batch_archive.py", str(root)]
            with patch.object(sys, "argv", arguments), \
                    patch.object(batch_archive, "create_archive", create), \
                    contextlib.redirect_stdout(stream):
                try:
                    batch_archive.main()
                except SystemExit as error:
                    exited = True
                    assert error.code == 1
            return stream.getvalue(), exited

        text, exited = run_main(failing)
        assert exited
        assert "error: boom" in text
        assert "done:" not in text

        text, exited = run_main(lambda *_args, **_kwargs: None)
        assert not exited
        assert f"done: {output}" in text

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "broken"
        root.mkdir()
        broken = root / "broken.zip"
        broken.touch()
        batch_archive.ensure_command = lambda _: None

        def failing_extract(command: list[str], _cwd: Path, _test: bool,
                            _input: str | None = None) -> None:
            raise subprocess.CalledProcessError(1, command)

        batch_archive.run = failing_extract
        try:
            batch_archive.expand_archives(root, [], [[]], False)
        except subprocess.CalledProcessError:
            pass
        else:
            raise AssertionError("extraction error was not raised")

        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            expanded = batch_archive.expand_archives(
                root, [], [[]], False, ignore_errors=True)
        assert expanded == []
        assert broken.exists()
        assert "warning: extraction failed" in stream.getvalue()


if __name__ == "__main__":
    main()
