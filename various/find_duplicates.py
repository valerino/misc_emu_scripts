#!/usr/bin/env python3
"""
Recursively scan a directory and report the absolute paths of files that have
the same MD5 hash (duplicates anywhere in the tree). Nothing is modified.

Files are grouped by size first, so only files that share a size with another
file are actually hashed.

Usage:
    python find_duplicates.py /path/to/dir
    python find_duplicates.py /path/to/dir --output dupes.txt
    python find_duplicates.py /path/to/dir --min-size 1048576    # ignore files < 1 MiB
"""
import argparse
import hashlib
import os
import sys
from collections import defaultdict
from pathlib import Path

CHUNK = 8 * 1024 * 1024  # 8 MiB, keeps memory low for big files


def md5_of(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        while chunk := f.read(CHUNK):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--output", "-o", type=Path, help="also write the report to this file")
    ap.add_argument("--min-size", type=int, default=1, metavar="BYTES",
                    help="ignore files smaller than this (default 1, i.e. skip empty files)")
    args = ap.parse_args()

    if not args.root.is_dir():
        sys.exit(f"Not a directory: {args.root}")

    root = args.root.resolve()
    errors = 0

    # 1) group by size
    by_size = defaultdict(list)
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            p = Path(dirpath) / name
            try:
                if p.is_symlink() or not p.is_file():
                    continue
                size = p.stat().st_size
            except OSError as e:
                print(f"ERROR stat {p}: {e}", file=sys.stderr)
                errors += 1
                continue
            if size >= args.min_size:
                by_size[size].append(p)

    # 2) hash only files that share a size, then group by MD5
    by_md5 = defaultdict(list)
    for size, paths in by_size.items():
        if len(paths) < 2:
            continue
        for p in paths:
            try:
                by_md5[(md5_of(p), size)].append(p)
            except OSError as e:
                print(f"ERROR read {p}: {e}", file=sys.stderr)
                errors += 1

    groups = sorted(
        ((digest, size, sorted(paths)) for (digest, size), paths in by_md5.items() if len(paths) > 1),
        key=lambda g: g[2][0],
    )

    lines = []
    wasted = 0
    for digest, size, paths in groups:
        lines.append(f"MD5 {digest} ({size} bytes, {len(paths)} files)")
        lines.extend(f"  {p}" for p in paths)
        lines.append("")
        wasted += size * (len(paths) - 1)

    lines.append(f"{len(groups)} duplicate group(s), "
                 f"{sum(len(g[2]) for g in groups)} files, "
                 f"{wasted / 1024 / 1024:.1f} MiB reclaimable, {errors} error(s)")

    report = "\n".join(lines)
    print(report)
    if args.output:
        args.output.write_text(report + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
