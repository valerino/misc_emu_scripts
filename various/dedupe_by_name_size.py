#!/usr/bin/env python3
"""
Find duplicate files by SIMILAR NAME + SAME SIZE (no hashing), recursively.
For each group, the newest file is kept and you are asked whether to delete
each older one. Directories left empty by a deletion are removed too
(cascading upwards, but never the start directory itself).

Every candidate group is then CONFIRMED with an MD5 check: only files whose
MD5 is really identical are treated as duplicates. Files that match by name
and size but differ in content are reported and never deleted.

Similar name = same extension and same normalized base name (case-folded,
everything except letters/digits ignored), so "Game_Name-(USA).chd",
"game name (usa).CHD" and "GAME NAME (USA).chd" match, but "Disc 1" and
"Disc 2" do not.

Name + size only selects the candidates (so big files are not hashed needlessly);
MD5 decides.

Usage:
    python dedupe_by_name_size.py /path/to/dir               # asks y/n for each older file
    python dedupe_by_name_size.py /path/to/dir --yes         # delete automatically, no questions
    python dedupe_by_name_size.py /path/to/dir --dry-run     # only show what would happen
    python dedupe_by_name_size.py /path/to/dir --protect-ext chd
    python dedupe_by_name_size.py /path/to/dir --similarity 0.9   # also match near-identical names
"""
import argparse
import difflib
import hashlib
import os
import re
import sys
from collections import defaultdict
from pathlib import Path


CHUNK = 8 * 1024 * 1024


def md5_of(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        while chunk := f.read(CHUNK):
            h.update(chunk)
    return h.hexdigest()


def normalize(stem: str) -> str:
    return re.sub(r"[\W_]+", "", stem.casefold()) or stem.casefold()


def cluster(items, similarity):
    """items: [(normalized_stem, Path)] sharing size+extension -> clusters of size >= 2."""
    n = len(items)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    by_key = defaultdict(list)
    for i, (k, _) in enumerate(items):
        by_key[k].append(i)
    for idxs in by_key.values():
        for j in idxs[1:]:
            parent[find(j)] = find(idxs[0])

    if similarity < 1.0:
        keys = list(by_key)
        sm = difflib.SequenceMatcher(autojunk=False)
        for a_i, a in enumerate(keys):
            sm.set_seq2(a)
            for b in keys[a_i + 1:]:
                sm.set_seq1(b)
                if (sm.real_quick_ratio() >= similarity and sm.quick_ratio() >= similarity
                        and sm.ratio() >= similarity):
                    parent[find(by_key[b][0])] = find(by_key[a][0])

    out = defaultdict(list)
    for i, (_, p) in enumerate(items):
        out[find(i)].append(p)
    return [v for v in out.values() if len(v) > 1]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", type=Path)
    ap.add_argument("--yes", "-y", action="store_true", help="automatically answer yes to every deletion")
    ap.add_argument("--dry-run", action="store_true", help="show what would be deleted, ask and delete nothing")
    ap.add_argument("--protect-ext", action="append", default=[], metavar="EXT",
                    help="never delete files with this extension (e.g. chd). Repeatable")
    ap.add_argument("--similarity", type=float, default=1.0, metavar="R",
                    help="also match names with normalized similarity >= R (0-1). Default 1.0 = exact after normalization. "
                         "Careful: low values can match 'Disc 1' with 'Disc 2'")
    args = ap.parse_args()

    if not args.root.is_dir():
        sys.exit(f"Not a directory: {args.root}")
    if not 0 < args.similarity <= 1:
        ap.error("--similarity must be in (0, 1]")

    root = args.root.resolve()
    protect = {"." + e.lower().lstrip(".") for e in args.protect_ext}

    # 1) bucket by (size, extension)
    buckets = defaultdict(list)
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            p = Path(dirpath) / name
            try:
                if p.is_symlink() or not p.is_file():
                    continue
                size = p.stat().st_size
            except OSError as e:
                print(f"ERROR stat {p}: {e}")
                continue
            if size == 0:
                continue  # empty files are not meaningful duplicates
            buckets[(size, p.suffix.casefold())].append((normalize(p.stem), p))

    groups = []
    for (size, _ext), items in buckets.items():
        if len(items) > 1:
            for c in cluster(items, args.similarity):
                groups.append((size, c))
    groups.sort(key=lambda g: sorted(g[1])[0])

    # 2) review groups
    removed = set()          # files (or dirs) deleted / that would be
    n_files = freed = n_dirs = n_protected = errors = n_groups = n_mismatch = 0
    auto = args.yes
    quit_now = False

    def remove_empty_dirs(start: Path):
        nonlocal n_dirs, errors
        d = start
        while d != root and root in d.parents:
            try:
                remaining = [e for e in os.scandir(d) if Path(e.path) not in removed]
            except OSError:
                return
            if remaining:
                return
            print(f"  {'WOULD REMOVE' if args.dry_run else 'REMOVE'} empty directory: {d}")
            if not args.dry_run:
                try:
                    d.rmdir()
                except OSError as e:
                    print(f"  ERROR removing {d}: {e}")
                    errors += 1
                    return
            removed.add(d)
            n_dirs += 1
            d = d.parent

    for size, paths in groups:
        paths = [p for p in paths if p.is_file()]
        if len(paths) < 2:
            continue

        # MD5 confirmation: split the name+size candidates by real content
        by_md5 = defaultdict(list)
        for p in paths:
            try:
                by_md5[md5_of(p)].append(p)
            except OSError as e:
                print(f"ERROR reading {p}: {e}")
                errors += 1
        confirmed = [(d, m) for d, m in by_md5.items() if len(m) > 1]
        unconfirmed = [p for m in by_md5.values() if len(m) == 1 for p in m]

        if unconfirmed and (confirmed or len(by_md5) > 1):
            n_mismatch += 1
            print(f"\nSAME NAME + SIZE BUT CONTENT DIFFERS ({size} bytes); only files with equal MD5 count as duplicates:")
            for d, m in sorted(by_md5.items(), key=lambda kv: str(kv[1][0])):
                for p in m:
                    print(f"  md5 {d}  {p}")
        if not confirmed:
            continue

        for digest, members in confirmed:
            members.sort(key=lambda p: (-p.stat().st_mtime, str(p)))
            keep, older = members[0], members[1:]
            n_groups += 1
            print(f"\nDUPLICATES CONFIRMED BY MD5 {digest} ({size} bytes)")
            print(f"  KEEP (newest): {keep}")
            for p in older:
                if p.suffix.lower() in protect:
                    print(f"  PROTECTED (not deleted): {p}")
                    n_protected += 1
                    continue
                if args.dry_run:
                    print(f"  WOULD DELETE older: {p}")
                else:
                    if not auto:
                        try:
                            ans = input(f"  Delete older file '{p}'? [y/N/a=yes to all/q=quit] ").strip().lower()
                        except EOFError:
                            ans = "q"
                        if ans == "q":
                            quit_now = True
                            break
                        if ans == "a":
                            auto = True
                        elif ans != "y":
                            continue
                    if not keep.is_file():
                        print(f"  ABORT group: kept file vanished: {keep}")
                        break
                    try:
                        p.unlink()
                        print(f"  DELETED: {p}")
                    except OSError as e:
                        print(f"  ERROR deleting {p}: {e}")
                        errors += 1
                        continue
                removed.add(p)
                n_files += 1
                freed += size
                remove_empty_dirs(p.parent)
            if quit_now:
                break
        if quit_now:
            print("\nStopped by user.")
            break

    print(f"\nDone: {len(groups)} name+size candidate group(s), {n_groups} confirmed by MD5, "
          f"{n_mismatch} with differing content (left alone), {n_files} file(s) "
          f"{'would be deleted' if args.dry_run else 'deleted'} ({freed / 1024 / 1024:.1f} MiB), "
          f"{n_dirs} empty director{'y' if n_dirs == 1 else 'ies'} {'would be removed' if args.dry_run else 'removed'}, "
          f"{n_protected} protected, {errors} error(s)")


if __name__ == "__main__":
    main()
