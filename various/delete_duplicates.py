#!/usr/bin/env python3
"""
Take the report produced by find_duplicates.py and, for every duplicate group,
delete the OLDER copies (by modification time), keeping only the newest.
Then remove directories left empty, or left containing nothing but .pdf files.

Safety rules (built for collections where .chd files must not be lost):
  * Dry run by default; nothing happens without --apply.
  * Before deleting, every file in a group is re-hashed (MD5). Files that no
    longer exist or no longer match the report are left alone. At least one
    verified identical copy is always kept. (--trust-report skips re-hashing.)
  * A directory is removed ONLY if it is empty, or contains only .pdf files
    (no subdirectories, no other files, no hidden files). Anything else,
    including any .chd, keeps the directory.
  * --protect-ext chd never deletes .chd files as "older duplicates",
    only reports them. (Repeat the option for more extensions.)
  * --root DIR refuses to touch anything outside DIR and enables cascading:
    after removing a directory, its parent is checked the same way, up to
    (never including) DIR. Without --root there is no cascading.

Usage:
    python find_duplicates.py /data -o dupes.txt
    python delete_duplicates.py dupes.txt --root /data                       # dry run
    python delete_duplicates.py dupes.txt --root /data --protect-ext chd     # dry run, chd untouched
    python delete_duplicates.py dupes.txt --root /data --apply               # really delete
    python find_duplicates.py /data | python delete_duplicates.py - --root /data
"""
import argparse
import hashlib
import os
import re
import sys
from pathlib import Path

CHUNK = 8 * 1024 * 1024
HEADER = re.compile(r"^MD5 ([0-9a-f]{32}) \((\d+) bytes")


def md5_of(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        while chunk := f.read(CHUNK):
            h.update(chunk)
    return h.hexdigest()


def parse_report(text: str):
    """-> list of (md5, size, [Path, ...])"""
    groups, cur = [], None
    for line in text.splitlines():
        m = HEADER.match(line)
        if m:
            cur = (m.group(1), int(m.group(2)), [])
            groups.append(cur)
        elif cur is not None and line.startswith("  ") and line.strip():
            cur[2].append(Path(line[2:]))
        elif not line.strip():
            cur = None
    return groups


def inside(path: Path, root: Path) -> bool:
    return root in path.parents


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report", help="find_duplicates.py output file, or - for stdin")
    ap.add_argument("--apply", action="store_true", help="really delete (default: dry run)")
    ap.add_argument("--root", type=Path, help="only touch files below this directory; enables cascading directory cleanup")
    ap.add_argument("--protect-ext", action="append", default=[], metavar="EXT",
                    help="never delete files with this extension as duplicates (e.g. chd). Repeatable")
    ap.add_argument("--trust-report", action="store_true", help="don't re-hash files before deleting (faster, less safe)")
    args = ap.parse_args()

    text = sys.stdin.read() if args.report == "-" else Path(args.report).read_text(encoding="utf-8")
    groups = parse_report(text)
    if not groups:
        sys.exit("No duplicate groups found in the report.")

    root = args.root.resolve() if args.root else None
    if root and not root.is_dir():
        sys.exit(f"Not a directory: {root}")
    protect = {"." + e.lower().lstrip(".") for e in args.protect_ext}

    removed_files = set()      # files deleted (or that would be, in a dry run)
    removed_dirs = set()
    touched_dirs = set()
    n_files = freed = n_protected = n_skipped = errors = 0
    n_dirs = n_pdfs = 0
    verb = "DELETE" if args.apply else "WOULD DELETE"

    # ------------------------------------------------ 1) duplicate files
    for md5, size, paths in groups:
        members = []
        for p in paths:
            if root and not inside(p.resolve(), root):
                print(f"SKIP (outside --root): {p}")
                n_skipped += 1
            elif not p.is_file() or p.is_symlink():
                print(f"SKIP (missing): {p}")
                n_skipped += 1
            else:
                members.append(p)

        if not args.trust_report:
            verified = []
            for p in members:
                try:
                    if md5_of(p) == md5:
                        verified.append(p)
                    else:
                        print(f"SKIP (content changed since report): {p}")
                        n_skipped += 1
                except OSError as e:
                    print(f"ERROR reading {p}: {e}")
                    errors += 1
            members = verified

        if len(members) < 2:
            continue

        members.sort(key=lambda p: (-p.stat().st_mtime, str(p)))
        keep, older = members[0], members[1:]
        print(f"\nDUPLICATES md5 {md5} ({size} bytes)")
        print(f"  KEEP  (newest): {keep}")
        for p in older:
            if p.suffix.lower() in protect:
                print(f"  PROTECTED (not deleted): {p}")
                n_protected += 1
                continue
            if not keep.is_file():   # last-moment sanity check
                print(f"  ABORT group: kept file vanished: {keep}")
                break
            print(f"  {verb}: {p}")
            if args.apply:
                try:
                    p.unlink()
                except OSError as e:
                    print(f"  ERROR deleting {p}: {e}")
                    errors += 1
                    continue
            removed_files.add(p)
            touched_dirs.add(p.parent)
            n_files += 1
            freed += size

    # ------------------------------------------------ 2) directory cleanup
    def classify(d: Path):
        """-> (removable, pdf files to delete first). Conservative on purpose."""
        pdfs = []
        try:
            entries = [e for e in os.scandir(d)]
        except OSError:
            return False, []
        for e in entries:
            ep = Path(e.path)
            if ep in removed_files or ep in removed_dirs:
                continue
            if e.is_symlink() or not e.is_file(follow_symlinks=False) or not e.name.lower().endswith(".pdf"):
                return False, []
            pdfs.append(ep)
        return True, pdfs

    def try_remove(d: Path) -> bool:
        nonlocal n_dirs, n_pdfs, errors
        if root and not (inside(d.resolve(), root)):
            return False
        ok, pdfs = classify(d)
        if not ok:
            return False
        what = "empty" if not pdfs else f"only {len(pdfs)} pdf file(s)"
        print(f"\n{verb} DIRECTORY ({what}): {d}")
        for pdf in pdfs:
            print(f"  {verb}: {pdf}")
        if args.apply:
            try:
                for pdf in pdfs:
                    pdf.unlink()
                d.rmdir()          # rmdir refuses non-empty dirs: extra safety net
            except OSError as e:
                print(f"  ERROR removing {d}: {e}")
                errors += 1
                return False
        removed_files.update(pdfs)
        removed_dirs.add(d)
        n_dirs += 1
        n_pdfs += len(pdfs)
        return True

    for d in sorted(touched_dirs, key=lambda p: (-len(p.parts), str(p))):
        if d in removed_dirs:
            continue
        cur = d
        while try_remove(cur):
            if not root:
                break               # no cascading without --root
            cur = cur.parent
            if cur == root or root not in cur.parents:
                break

    print(f"\nDone: {n_files} duplicate file(s) {'deleted' if args.apply else 'would be deleted'} "
          f"({freed / 1024 / 1024:.1f} MiB), {n_dirs} director{'y' if n_dirs == 1 else 'ies'} "
          f"{'removed' if args.apply else 'would be removed'} (incl. {n_pdfs} pdf), "
          f"{n_protected} protected, {n_skipped} skipped, {errors} error(s)"
          + ("" if args.apply else " (dry run, use --apply)"))


if __name__ == "__main__":
    main()
