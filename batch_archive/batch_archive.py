#!/usr/bin/env python3
"""Expand ZIP/7z/LHA/TAR.GZ files in a directory, then create one ZIP or 7z archive.

Examples:
  batch_archive.py roms
  batch_archive.py roms --format 7z --output /archives/roms.7z
  batch_archive.py roms --no-touch keep.txt --delete

Patterns are gitignore-like: blank lines and lines beginning with # are ignored,
and a leading ! re-includes a path matched by an earlier pattern.  Patterns with
a slash are matched relative to the input directory; other patterns match either
the relative path or its basename.
"""

import argparse
import fnmatch
import shutil
import subprocess
from pathlib import Path


ARCHIVE_SUFFIXES = {".zip", ".7z", ".lha", ".tar.gz"}


def archive_suffix(path: Path) -> str | None:
    """Return the archive suffix of path, matching .tar.gz before single suffixes."""
    name = path.name.lower()
    return next((suffix for suffix in ARCHIVE_SUFFIXES if name.endswith(suffix)), None)
ARG_BATCH_BYTES = 32_000


def read_patterns(path: Path) -> list[str]:
    """Read the small gitignore-style pattern file."""
    return [line.strip() for line in path.read_text().splitlines()
            if line.strip() and not line.lstrip().startswith("#")]


def no_touch_file(requested: Path | None) -> Path | None:
    """Use notouch.txt in the current directory when none was requested."""
    default = Path.cwd() / "notouch.txt"
    return requested or (default if default.is_file() else None)


def excluded(path: Path, root: Path, patterns: list[str]) -> bool:
    """Return whether path is excluded by the last matching pattern."""
    relative = path.relative_to(root).as_posix()
    result = False
    for raw_pattern in patterns:
        include = raw_pattern.startswith("!")
        pattern = raw_pattern[1:] if include else raw_pattern
        pattern = pattern.lstrip("/")
        if pattern.endswith("/"):
            directory = pattern.rstrip("/")
            match = relative == directory or relative.startswith(directory + "/")
        elif "/" in pattern:
            match = fnmatch.fnmatchcase(relative, pattern)
        else:
            match = (fnmatch.fnmatchcase(relative, pattern) or
                     fnmatch.fnmatchcase(path.name, pattern))
        if match:
            result = not include
    return result


def protected(path: Path, root: Path, pattern_files: list[list[str]]) -> bool:
    """Return whether any independent ignore file protects path."""
    return any(excluded(path, root, patterns) for patterns in pattern_files)


def print_command(command: list[str], cwd: Path) -> None:
    """Show the exact external operation before running it."""
    print(f"$ (cd {cwd} && {shlex_join(command)})", flush=True)


def shlex_join(command: list[str]) -> str:
    """Use stdlib quoting while retaining Python 3.7 compatibility."""
    try:
        import shlex
        return shlex.join(command)
    except AttributeError:
        import shlex
        return " ".join(shlex.quote(item) for item in command)


def run(command: list[str], cwd: Path, test: bool, input_text: str | None = None) -> None:
    print_command(command, cwd)
    if not test:
        subprocess.run(command, cwd=cwd, check=True, input=input_text, text=input_text is not None)


def ensure_command(name: str) -> None:
    if shutil.which(name) is None:
        raise SystemExit(f"error: required command not found: {name}")


def extract_destination(archive: Path, lha_tag: bool) -> Path:
    """Return the directory used for an archive's extracted files."""
    destination = archive.with_name(archive.name[:-len(archive_suffix(archive))])
    return destination.with_name(destination.name + "-lha") if lha_tag and archive.suffix.lower() == ".lha" else destination


def expand_archives(root: Path, expanded: list[Path], pattern_files: list[list[str]], test: bool,
                    lha_tag: bool = True) -> list[Path]:
    """Extract archives, including archives revealed by earlier extraction."""
    while archives := [path for path in root.rglob("*")
                       if path.is_file() and archive_suffix(path)
                       and extract_destination(path, lha_tag) not in expanded
                       and not protected(path, root, pattern_files)]:
        for archive in archives:
            suffix = archive_suffix(archive)
            destination = extract_destination(archive, lha_tag)
            if suffix == ".zip":
                ensure_command("unzip")
                command = ["unzip", "-o", str(archive), "-d", str(destination)]
            elif suffix == ".tar.gz":
                ensure_command("tar")
                command = ["tar", "-xzf", str(archive), "-C", str(destination)]
                if not test:
                    destination.mkdir(exist_ok=True)
            elif suffix == ".lha":
                ensure_command("7z")
                command = ["7z", "x", str(archive)]
                if not test:
                    destination.mkdir(exist_ok=True)
            else:
                ensure_command("7z")
                command = ["7z", "x", "-y", f"-o{destination}", str(archive)]
            print(f"extracting {archive} to {destination}", flush=True)
            expanded.append(destination)
            run(command, destination if suffix == ".lha" else root, test)
    return expanded


def output_path(root: Path, requested: str | None, archive_format: str) -> Path:
    """Default to a sibling archive so it can never archive or delete itself."""
    if requested:
        return Path(requested).expanduser().resolve()
    return root.parent / f"{root.name}.{archive_format}"


def backup_path(root: Path) -> Path:
    """Store the optional input backup beside the input directory."""
    return root.with_name(root.name + ".backup")


def backup_input(root: Path, test: bool) -> None:
    """Copy the original input before extraction can change it."""
    destination = backup_path(root)
    if destination.exists():
        raise SystemExit(f"error: backup already exists: {destination}")
    print(f"backing up {root} to {destination}", flush=True)
    if not test:
        shutil.copytree(root, destination, symlinks=True)


def is_inside(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
        return True
    except ValueError:
        return False


def extracted_source(path: Path, expanded: list[Path], lha_tag: bool) -> bool:
    """Return whether path is a source archive that was already extracted."""
    return (archive_suffix(path)
            and extract_destination(path, lha_tag) in expanded)


def excluded_from_archive(path: Path, root: Path, expanded: list[Path],
                          pattern_files: list[list[str]], lha_tag: bool) -> bool:
    """Return whether path is kept out of the output archive."""
    return protected(path, root, pattern_files) or extracted_source(path, expanded, lha_tag)


def archive_batches(root: Path, expanded: list[Path],
                    pattern_files: list[list[str]], lha_tag: bool = True):
    """Yield bounded argument batches without newline-delimited file lists."""
    batch: list[tuple[Path, str]] = []
    size = 0
    for path in root.rglob("*"):
        if not path.is_file() or excluded_from_archive(path, root, expanded, pattern_files, lha_tag):
            continue
        name = "./" + path.relative_to(root).as_posix()
        if batch and size + len(name) + 1 > ARG_BATCH_BYTES:
            yield batch
            batch = []
            size = 0
        batch.append((path, name))
        size += len(name) + 1
    if batch:
        yield batch


def unsafe_7z_path(root: Path, expanded: list[Path],
                   pattern_files: list[list[str]], lha_tag: bool = True) -> Path | None:
    """Return a path whose newline 7z would silently rewrite."""
    return next((path for path in root.rglob("*")
                 if path.is_file()
                 and not excluded_from_archive(path, root, expanded, pattern_files, lha_tag)
                 and ("\n" in path.name or "\r" in path.name)), None)


def create_archive(root: Path, output: Path, archive_format: str,
                   pattern_files: list[list[str]], expanded: list[Path],
                   test: bool, delete: bool = False,
                   lha_tag: bool = True) -> None:
    """Archive every included file using the requested native command."""
    if archive_format == "zip":
        ensure_command("zip")
    else:
        ensure_command("7z")
        if unsafe_path := unsafe_7z_path(root, expanded, pattern_files, lha_tag):
            raise SystemExit(f"error: 7z cannot safely archive newline in filename: {unsafe_path}")

    if output.exists():
        print(f"removing existing output {output}", flush=True)
        if not test:
            output.unlink()
    print(f"creating {output} from {root}", flush=True)
    created = False
    for batch in archive_batches(root, expanded, pattern_files, lha_tag):
        names = [name for _, name in batch]
        if archive_format == "zip":
            run(["zip", "-q", str(output), *names], root, test)
        else:
            run(["7z", "a", "-spd", "--", str(output), *names], root, test)
        created = True
    if not created:
        raise SystemExit("error: no files remain after exclusions")
    if delete:
        if test:
            print(f"deleting input directory {root}", flush=True)
        else:
            for path in root.rglob("*"):
                if path.is_file() and not protected(path, root, pattern_files):
                    print(f"deleting {path}", flush=True)
                    path.unlink()
            delete_empty_directories(root, root, pattern_files, test, include_root=True)
    else:
        delete_extracted(root, expanded, pattern_files, test)


def delete_archived(files: list[Path], root: Path, pattern_files: list[list[str]],
                    test: bool) -> None:
    """Delete archived files and their now-empty subdirectories."""
    for path in files:
        if protected(path, root, pattern_files):
            continue
        print(f"deleting {path}", flush=True)
        if not test:
            path.unlink()
    delete_empty_directories(root, root, pattern_files, test)


def delete_empty_directories(directory: Path, root: Path,
                             pattern_files: list[list[str]], test: bool,
                             include_root: bool = False) -> None:
    """Delete unprotected empty directories, deepest first."""
    paths = [path for path in directory.rglob("*") if path != directory]
    if include_root:
        paths.append(directory)
    for path in sorted(paths, key=lambda path: len(path.parts), reverse=True):
        if (path.is_dir() and not protected(path, root, pattern_files)
                and not any(path.iterdir())):
            print(f"deleting {path}", flush=True)
            if not test:
                path.rmdir()


def delete_extracted(root: Path, expanded: list[Path],
                     pattern_files: list[list[str]], test: bool) -> None:
    """Remove unprotected extracted destination directories."""
    destinations = sorted(expanded, key=lambda path: len(path.parts), reverse=True)
    for destination in destinations:
        if not destination.exists():
            continue
        files = [path for path in destination.rglob("*")
                 if path.is_file() and not protected(path, root, pattern_files)]
        for path in files:
            print(f"deleting {path}", flush=True)
            if not test:
                path.unlink()
        for path in sorted(destination.rglob("*"), key=lambda path: len(path.parts), reverse=True):
            if path.is_dir() and not protected(path, root, pattern_files) and not any(path.iterdir()):
                print(f"deleting extracted {path}", flush=True)
                if not test:
                    path.rmdir()
        if not protected(destination, root, pattern_files) and not any(destination.iterdir()):
            print(f"deleting extracted {destination}", flush=True)
            if not test:
                destination.rmdir()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract ZIP/7z/LHA/TAR.GZ files, then archive a directory.",
        epilog="--delete removes everything except files matching --no-touch.",
    )
    parser.add_argument("directory", type=Path, help="directory to process recursively")
    parser.add_argument("--format", choices=("zip", "7z"), default="zip",
                        help="output format (default: zip)")
    parser.add_argument("-o", "--output", help="output path (default: INPUT_DIRECTORY.EXT beside it)")
    parser.add_argument("-d", "--delete", action="store_true",
                        help="delete the input after archiving, preserving only --no-touch files")
    parser.add_argument("-n", "--test", action="store_true",
                        help="print operations without changing files")
    parser.add_argument("--no-touch", type=Path, metavar="FILE",
        help="read gitignore-like patterns for paths never extracted or deleted")
    parser.add_argument("--no-lha-tag", action="store_true",
                        help="extract .lha files without the default -lha directory suffix")
    parser.add_argument("--backup", action="store_true",
                        help="copy the original input to INPUT_DIRECTORY.backup before processing")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.directory.expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"error: not a directory: {root}")
    pattern_files: list[list[str]] = [[]]
    pattern_file = no_touch_file(args.no_touch)
    if pattern_file:
        try:
            pattern_files = [read_patterns(pattern_file.expanduser())]
        except OSError as error:
            raise SystemExit(f"error: cannot read pattern file: {error}") from error

    output = output_path(root, args.output, args.format)
    if is_inside(output, root):
        raise SystemExit("error: output must be outside the input directory")

    if args.backup:
        backup_input(root, args.test)

    expanded: list[Path] = []
    try:
        expanded = expand_archives(root, expanded, pattern_files, args.test, not args.no_lha_tag)
        create_archive(root, output, args.format, pattern_files, expanded, args.test,
                    args.delete, not args.no_lha_tag)
    except (Exception, KeyboardInterrupt) as error:
        print(f"error: {error}, performing cleanup ...")
        delete_extracted(root, expanded, pattern_files, args.test)

    print("done", flush=True)


if __name__ == "__main__":
    main()
