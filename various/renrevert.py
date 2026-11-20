#!/usr/bin/env python3
"""
Revert renames done by rename_regions.py, using its output log.

Files whose removed tag was a language-code list like (En,Fr,De) are left
renamed. Everything else (Disc N, Rev N, M, Proto, G-Con45, ...) is restored.

The log's RENAME lines only contain file names, not directories, so each
renamed file is located by scanning the tree. rename_regions.py processed
files in sorted(rglob) order, so the k-th log entry for a given new name is
matched with the k-th file of that name found in the same sorted order.
If the counts don't match for a name, that name is skipped and reported.

Usage:
    python revert_renames.py /path/to/dir renames.log            # dry run
    python revert_renames.py /path/to/dir renames.log --apply    # do it
"""
import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

# Language-code group such as "En", "En,Fr", "En,Fr,De,Es,It"
LANG = re.compile(r"^[A-Z][a-z](?:,[A-Z][a-z])*$")


def has_language_codes(name: str) -> bool:
    return any(LANG.match(g) for g in re.findall(r"\(([^()]*)\)", name))


def parse_log(log_path: Path):
    entries = defaultdict(list)  # new_name -> [old_name, ...] in log order
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not (line.startswith("RENAME: ") or line.startswith("WOULD RENAME: ")):
            continue  # ignore SKIP lines and the summary
        old, sep, new = line.split("RENAME: ", 1)[1].partition(" -> ")
        if sep:
            entries[new].append(old)
    return entries


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("log", type=Path)
    ap.add_argument("--apply", action="store_true", help="perform the reverts (default: dry run)")
    args = ap.parse_args()

    if not args.root.is_dir():
        sys.exit(f"Not a directory: {args.root}")
    if not args.log.is_file():
        sys.exit(f"Log file not found: {args.log}")

    entries = parse_log(args.log)

    by_name = defaultdict(list)
    for p in sorted(args.root.rglob("*")):  # same order as rename_regions.py
        if p.is_file() and p.name in entries:
            by_name[p.name].append(p)

    reverted = kept = skipped = 0
    for new_name, olds in entries.items():
        found = by_name.get(new_name, [])
        if len(found) != len(olds):
            print(f"MISMATCH (log: {len(olds)}, found: {len(found)}), skipping: {new_name}")
            skipped += len(olds)
            continue

        for path, old_name in zip(found, olds):
            if has_language_codes(old_name):
                kept += 1
                continue
            target = path.with_name(old_name)
            if target.exists():
                print(f"SKIP (target exists): {path} -> {old_name}")
                skipped += 1
                continue
            print(f"{'REVERT' if args.apply else 'WOULD REVERT'}: {path.parent}/ {path.name} -> {old_name}")
            if args.apply:
                path.rename(target)
            reverted += 1

    print(f"\nDone: {reverted} reverted, {kept} kept (language codes), {skipped} skipped"
          + ("" if args.apply else " (dry run, use --apply)"))


if __name__ == "__main__":
    main()

