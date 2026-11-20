#!/usr/bin/env python3
"""
Recursively strip language-code groups like (En,Fr,De,Es,It) from file names,
whatever the region tag is and wherever the group sits in the name:
    Game (Europe) (En,Fr,De).zip      ->  Game (Europe).zip
    Game (USA) (En,Es) (Rev 1).chd    ->  Game (USA) (Rev 1).chd
    Game (Japan) (En,Ja).chd          ->  Game (Japan).chd

Only the language-code group is removed; all other tags are kept.
Files without a language-code group are left untouched.

Usage:
    python rename_regions_lang.py /path/to/dir            # dry run (default)
    python rename_regions_lang.py /path/to/dir --apply    # actually rename
"""
import argparse
import re
import sys
from pathlib import Path

# A language-code group: "(En)", "(En,Ja)", "(En,Fr,De,Es,It)", ... with its leading space
LANG_GROUP = re.compile(r"\s*\([A-Z][a-z](?:,[A-Z][a-z])*\)")


def new_name_for(path: Path):
    stem, ext = path.stem, path.suffix
    new_stem = LANG_GROUP.sub("", stem)
    new_stem = re.sub(r"\s{2,}", " ", new_stem).strip()
    if new_stem == stem or not new_stem:
        return None
    return new_stem + ext


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
        new_name = new_name_for(path)
        if not new_name:
            continue

        new_path = path.with_name(new_name)
        if new_path.exists():
            print(f"SKIP (target exists): {path} -> {new_name}")
            skipped += 1
            continue

        print(f"{'RENAME' if args.apply else 'WOULD RENAME'}: {path.name} -> {new_name}")
        if args.apply:
            path.rename(new_path)
        renamed += 1

    print(f"\nDone: {renamed} renamed, {skipped} skipped" + ("" if args.apply else " (dry run, use --apply)"))


if __name__ == "__main__":
    main()

