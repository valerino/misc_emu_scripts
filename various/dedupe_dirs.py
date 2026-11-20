#!/usr/bin/env python3
"""
Recursively scan a folder. Inside each directory, find files with the same
size, compute their MD5, and if the MD5 matches, delete the older copies
(by modification time), keeping only the newest one.

Duplicates are only searched within the same directory, never across
directories.

Usage:
    python dedupe_dirs.py /path/to/dir            # dry run (default)
    python dedupe_dirs.py /path/to/dir --apply    # actually delete
"""
import argparse
import hashlib
import os
import sys
from collections import defaultdict
from pathlib import Path

CHUNK = 8 * 1024 * 1024  # 8 MiB, keeps memory low for big files (e.g. CHD/ISO)


def md5_of(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        while chunk := f.read(CHUNK):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--apply", action="store_true", help="delete duplicates (default: dry run)")
    args = ap.parse_args()

    if not args.root.is_dir():
        sys.exit(f"Not a directory: {args.root}")

    deleted = freed = errors = 0

    for dirpath, _dirnames, filenames in os.walk(args.root):
        files = [Path(dirpath) / n for n in filenames]
        files = [p for p in files if p.is_file() and not p.is_symlink()]
        if len(files) < 2:
            continue

        # 1) group by size, only same-size files can be identical
        by_size = defaultdict(list)
        for p in files:
            try:
                by_size[p.stat().st_size].append(p)
            except OSError as e:
                print(f"ERROR stat {p}: {e}")
                errors += 1

        for size, same_size in by_size.items():
            if len(same_size) < 2:
                continue

            # 2) group same-size files by MD5
            by_md5 = defaultdict(list)
            for p in same_size:
                try:
                    by_md5[md5_of(p)].append(p)
                except OSError as e:
                    print(f"ERROR read {p}: {e}")
                    errors += 1

            # 3) in each identical group keep the newest, delete the rest
            for digest, group in by_md5.items():
                if len(group) < 2:
                    continue
                # newest mtime first; name as a stable tie-breaker
                group.sort(key=lambda p: (-p.stat().st_mtime, p.name))
                keep, older = group[0], group[1:]
                print(f"DUPLICATES (md5 {digest}, {size} bytes) in {keep.parent}")
                print(f"  KEEP   : {keep.name}")
                for p in older:
                    print(f"  {'DELETE' if args.apply else 'WOULD DELETE'}: {p.name}")
                    if args.apply:
                        try:
                            p.unlink()
                        except OSError as e:
                            print(f"  ERROR deleting {p}: {e}")
                            errors += 1
                            continue
                    deleted += 1
                    freed += size

    print(f"\nDone: {deleted} file(s) {'deleted' if args.apply else 'would be deleted'}, "
          f"{freed / 1024 / 1024:.1f} MiB {'freed' if args.apply else 'reclaimable'}, {errors} error(s)"
          + ("" if args.apply else " (dry run, use --apply)"))


if __name__ == "__main__":
    main()

