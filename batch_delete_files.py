#!/usr/bin/env python3
"""Recursively delete files and nested directories, preserving top-level directories."""

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory


def delete_files(directory: Path, dry_run: bool = False, delete_directories: bool = True) -> int:
    """Delete files and, by default, directories below the top level; return the file count."""
    if not directory.is_dir():
        raise NotADirectoryError(directory)

    files = [path for path in directory.rglob("*") if not path.is_dir() or path.is_symlink()]
    for path in files:
        if not dry_run:
            path.unlink()
            print(f"Deleted: {path}")
    if delete_directories and not dry_run:
        directories = (path for path in directory.rglob("*")
                       if path.is_dir() and not path.is_symlink() and path.parent != directory)
        for path in sorted(directories, key=lambda path: len(path.parts), reverse=True):
            path.rmdir()
            print(f"Deleted: {path}")
    return len(files)


def self_test() -> None:
    with TemporaryDirectory() as temp:
        root = Path(temp)
        top_level = root / "top-level"
        nested = top_level / "nested"
        nested.mkdir(parents=True)
        (root / "one.txt").touch()
        (nested / "two.txt").touch()
        assert delete_files(root, dry_run=True) == 2
        assert (root / "one.txt").exists()
        assert delete_files(root) == 2
        assert root.is_dir() and top_level.is_dir() and not nested.exists()
        nested.mkdir()
        (nested / "three.txt").touch()
        assert delete_files(root, delete_directories=False) == 1
        assert top_level.is_dir() and nested.is_dir()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", nargs="?", type=Path)
    parser.add_argument("--dry-run", action="store_true", help="show how many files would be deleted")
    parser.add_argument("--no-delete-directories", action="store_true",
                        help="preserve all directories")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
    elif args.directory is None:
        parser.error("directory is required unless --self-test is used")
    else:
        count = delete_files(args.directory, args.dry_run, not args.no_delete_directories)
        print(f"{'Would delete' if args.dry_run else 'Deleted'} {count} file(s).")
