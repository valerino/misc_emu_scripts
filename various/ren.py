#!/usr/bin/env python3
"""
Recursively rename files like:
    Game (EUR) (En,Fr,De).zip   ->  Game (EUR).zip
    Game (USA) (Rev 1).zip      ->  Game (USA).zip

Usage:
    python rename_regions.py /path/to/dir            # dry run (default)
    python rename_regions.py /path/to/dir --apply    # actually rename
"""
import argparse
import re
import sys
from pathlib import Path

# "(EUR)" or "(USA)" followed by one or more " (something)" groups, then ".ext"
PATTERN = re.compile(r"^(?P<base>.*\((?:EUR|USA)\))(?:\s+\([^()]*\))+(?P<ext>\.[^.]+)$")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--apply", action="store_true", help="perform the renames (default: dry run)")
    args = ap.parse_args()

    if not args.root.is_dir():
        sys.exit(f"Not a directory: {args.root}")

    renamed = skipped = 0
    for path in sorted(args.root.rglob("*")):
        if not path.is_file():
            continue
        m = PATTERN.match(path.name)
        if not m:
            continue

        new_path = path.with_name(m["base"] + m["ext"])
        if new_path.exists():
            print(f"SKIP (target exists): {path} -> {new_path.name}")
            skipped += 1
            continue

        print(f"{'RENAME' if args.apply else 'WOULD RENAME'}: {path.name} -> {new_path.name}")
        if args.apply:
            path.rename(new_path)
        renamed += 1

    print(f"\nDone: {renamed} renamed, {skipped} skipped" + ("" if args.apply else " (dry run, use --apply)"))


if __name__ == "__main__":
    main()

