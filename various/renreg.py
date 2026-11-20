#!/usr/bin/env python3
"""
Recursively rename only files whose trailing tags include a language-code list:
    Game (EUR) (En,Fr,De).zip        ->  Game (EUR).zip
    Game (USA) (En,Es) (Rev 1).chd   ->  Game (USA).chd

Files with other tags only, e.g. "Game (USA) (Disc 1).chd" or
"Game (USA) (Rev 1).chd", are left untouched.

Usage:
    python rename_regions_lang.py /path/to/dir            # dry run (default)
    python rename_regions_lang.py /path/to/dir --apply    # actually rename
"""
import argparse
import re
import sys
from pathlib import Path

# "(EUR)" or "(USA)" followed by one or more " (something)" groups, then ".ext"
PATTERN = re.compile(r"^(?P<base>.*\((?:EUR|USA)\))(?P<tags>(?:\s+\([^()]*\))+)(?P<ext>\.[^.]+)$")

# Language-code group such as "En", "En,Fr", "En,Fr,De,Es,It"
LANG = re.compile(r"^[A-Z][a-z](?:,[A-Z][a-z])*$")


def has_language_codes(tags: str) -> bool:
    return any(LANG.match(g) for g in re.findall(r"\(([^()]*)\)", tags))


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
        if not m or not has_language_codes(m["tags"]):
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

