#!/usr/bin/env python3
"""
Find directories with similar names and, optionally, check whether their
contents are identical (MD5) and delete the OLDER copy.

Name similarity: names are normalized (case-folded, everything except letters
and digits removed), so "Final Fantasy VII", "final_fantasy-vii" and
"FINAL.FANTASY.VII" all match. With --similarity R (0-1) names that are
merely close (e.g. extra words/characters) also match.
By default only SIBLING directories (same parent) are compared; use
--anywhere to compare across the whole tree.

Step 1 - find and save candidates:
    python similar_dirs.py /start/dir --find-similar groups.json

Step 2 - check contents, report, and optionally delete older duplicates:
    python similar_dirs.py --groups groups.json --check-duplicates            # report only
    python similar_dirs.py --groups groups.json --check-duplicates --delete   # asks before each delete

Both steps at once (no file needed for step 2):
    python similar_dirs.py /start/dir --check-duplicates [--delete]

"Identical" = same set of (relative file path, MD5). Use --ignore-filenames
to compare only the multiset of file contents. "Older" = the directory whose
newest file has the oldest modification time (directory mtimes are unreliable).
Empty directories are never compared or deleted.

Directories where only SOME files match (partial matches) are reported with
the identical / different / missing files, but are never deleted.
"""
import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

CHUNK = 8 * 1024 * 1024


# ----------------------------------------------------------------- names ---
def normalize(name: str) -> str:
    return re.sub(r"[\W_]+", "", name.casefold()) or name.casefold()


def cluster_keys(buckets, similarity):
    """buckets: normalized key -> [paths]. Merge buckets with close keys."""
    keys = list(buckets)
    parent = {k: k for k in keys}

    def find(k):
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    if similarity < 1.0:
        sm = difflib.SequenceMatcher(autojunk=False)
        for i, a in enumerate(keys):
            sm.set_seq2(a)
            for b in keys[i + 1:]:
                sm.set_seq1(b)
                if (sm.real_quick_ratio() >= similarity and sm.quick_ratio() >= similarity
                        and sm.ratio() >= similarity):
                    parent[find(b)] = find(a)

    merged = defaultdict(list)
    for k in keys:
        merged[find(k)].extend(buckets[k])
    return [sorted(v) for v in merged.values() if len(v) > 1]


def find_similar(root: Path, anywhere: bool, similarity: float):
    per_scope = defaultdict(lambda: defaultdict(list))  # scope -> key -> paths
    for dirpath, dirnames, _ in os.walk(root):
        dirnames.sort()
        for d in dirnames:
            p = Path(dirpath) / d
            if p.is_symlink():
                continue
            scope = "" if anywhere else dirpath
            per_scope[scope][normalize(d)].append(p)

    groups = []
    for buckets in per_scope.values():
        groups.extend(cluster_keys(buckets, similarity))
    return sorted(groups)


# -------------------------------------------------------------- contents ---
def list_files(d: Path):
    """-> list of (relative posix path, size, Path, mtime)"""
    out = []
    for dirpath, _, fnames in os.walk(d):
        for f in fnames:
            p = Path(dirpath) / f
            if p.is_symlink() or not p.is_file():
                continue
            st = p.stat()
            out.append((p.relative_to(d).as_posix(), st.st_size, p, st.st_mtime))
    return out


_md5_cache = {}


def md5_of(path: Path) -> str:
    if path not in _md5_cache:
        h = hashlib.md5()
        with path.open("rb") as f:
            while chunk := f.read(CHUNK):
                h.update(chunk)
        _md5_cache[path] = h.hexdigest()
    return _md5_cache[path]


def related(a: Path, b: Path) -> bool:
    return a == b or a in b.parents or b in a.parents


def identical_classes(dirs, ignore_names):
    """Partition dirs into classes with identical contents; return classes of size >= 2."""
    info = {}
    for d in dirs:
        files = list_files(d)
        if files:
            info[d] = files

    # cheap pass: sizes only
    by_size_sig = defaultdict(list)
    for d, files in info.items():
        sig = (tuple(sorted(s for _, s, _, _ in files)) if ignore_names
               else tuple(sorted((r, s) for r, s, _, _ in files)))
        by_size_sig[sig].append(d)

    classes = []
    for candidates in by_size_sig.values():
        if len(candidates) < 2:
            continue
        by_md5_sig = defaultdict(list)
        for d in candidates:
            if ignore_names:
                sig = tuple(sorted(md5_of(p) for _, _, p, _ in info[d]))
            else:
                sig = tuple(sorted((r, md5_of(p)) for r, _, p, _ in info[d]))
            by_md5_sig[sig].append(d)
        classes.extend(c for c in by_md5_sig.values() if len(c) > 1)

    newest = {d: max(m for _, _, _, m in info[d]) for d in info}
    return classes, newest, info


def compare_partial(fa, fb, ignore_names):
    """Compare two file lists [(rel, size, path, mtime)]. Returns counts and lists."""
    if ignore_names:
        sizes_a = {s for _, s, _, _ in fa}
        sizes_b = {s for _, s, _, _ in fb}
        pool = defaultdict(list)            # (size, md5) -> [rel] of B files
        only_b = []
        for r, s, p, _ in fb:
            if s in sizes_a:
                pool[(s, md5_of(p))].append(r)
            else:
                only_b.append(r)
        matched, only_a = 0, []
        for r, s, p, _ in fa:
            key = (s, md5_of(p)) if s in sizes_b else None
            if key and pool.get(key):
                pool[key].pop()
                matched += 1
            else:
                only_a.append(r)
        only_b += [r for lst in pool.values() for r in lst]
        differing = []                      # not detectable without file names
    else:
        da = {r: (s, p) for r, s, p, _ in fa}
        db = {r: (s, p) for r, s, p, _ in fb}
        matched, differing = 0, []
        for r in sorted(da.keys() & db.keys()):
            if da[r][0] == db[r][0] and md5_of(da[r][1]) == md5_of(db[r][1]):
                matched += 1
            else:
                differing.append(r)
        only_a = sorted(da.keys() - db.keys())
        only_b = sorted(db.keys() - da.keys())
    return matched, differing, sorted(only_a), sorted(only_b)


def fmt_list(items, limit):
    shown = ", ".join(items[:limit])
    return shown + (f", ... (+{len(items) - limit} more)" if len(items) > limit else "")


# ------------------------------------------------------------------ main ---
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", type=Path, nargs="?", help="start directory (not needed with --groups)")
    ap.add_argument("--find-similar", metavar="FILE", type=Path,
                    help="scan for similarly named directories and save them to FILE (JSON)")
    ap.add_argument("--groups", metavar="FILE", type=Path,
                    help="load groups saved by --find-similar instead of scanning")
    ap.add_argument("--check-duplicates", action="store_true",
                    help="compare contents (MD5) of the similarly named directories")
    ap.add_argument("--delete", action="store_true",
                    help="with --check-duplicates: offer to delete the OLDER identical directory")
    ap.add_argument("--yes", action="store_true", help="with --delete: don't ask, delete right away")
    ap.add_argument("--anywhere", action="store_true", help="compare names across the whole tree, not only siblings")
    ap.add_argument("--similarity", type=float, default=1.0, metavar="R",
                    help="also match names whose normalized similarity is >= R (0-1, e.g. 0.9). Default 1.0 = exact after normalization")
    ap.add_argument("--ignore-filenames", action="store_true",
                    help="compare only file contents, not file names/paths")
    ap.add_argument("--max-list", type=int, default=5, metavar="N",
                    help="max file names listed per category in partial-match reports (default 5)")
    args = ap.parse_args()

    if not args.find_similar and not args.check_duplicates:
        ap.error("give --find-similar FILE and/or --check-duplicates")
    if args.delete and not args.check_duplicates:
        ap.error("--delete needs --check-duplicates")
    if not 0 < args.similarity <= 1:
        ap.error("--similarity must be in (0, 1]")

    # ---- get groups
    if args.groups:
        groups = [[Path(p) for p in g] for g in json.loads(args.groups.read_text(encoding="utf-8"))]
    else:
        if not args.root or not args.root.is_dir():
            sys.exit("A valid start directory is required (or use --groups FILE)")
        groups = find_similar(args.root.resolve(), args.anywhere, args.similarity)

    if args.find_similar:
        args.find_similar.write_text(
            json.dumps([[str(p) for p in g] for g in groups], indent=2, ensure_ascii=False),
            encoding="utf-8")
        print(f"Found {len(groups)} group(s) of similarly named directories -> {args.find_similar}")
        if not args.check_duplicates:
            for g in groups:
                print()
                for p in g:
                    print(f"  {p}")
            return

    # ---- compare contents
    found = deleted = partial = 0
    delete_all = args.yes
    for group in groups:
        dirs = [d for d in group if d.is_dir()]
        if len(dirs) < 2:
            continue
        classes, newest, info = identical_classes(dirs, args.ignore_filenames)
        for cls in classes:
            if any(related(a, b) for i, a in enumerate(cls) for b in cls[i + 1:]):
                print(f"\nSKIP (one directory contains another): {', '.join(map(str, cls))}")
                continue
            cls.sort(key=lambda d: (-newest[d], str(d)))
            keep, older = cls[0], cls[1:]
            found += 1
            print(f"\nIDENTICAL CONTENTS ({len(list_files(keep))} files)")
            print(f"  KEEP  (newest): {keep}")
            for d in older:
                print(f"  OLDER         : {d}")

            if not args.delete:
                continue
            for d in older:
                if not d.is_dir():
                    continue
                if not delete_all:
                    ans = input(f"  Delete OLDER directory '{d}'? [y/N/a=all/q=quit] ").strip().lower()
                    if ans == "q":
                        print(f"\nStopped. {deleted} director{'y' if deleted == 1 else 'ies'} deleted.")
                        return
                    if ans == "a":
                        delete_all = True
                    elif ans != "y":
                        continue
                try:
                    shutil.rmtree(d)
                    print(f"  DELETED: {d}")
                    deleted += 1
                except OSError as e:
                    print(f"  ERROR deleting {d}: {e}")

        # ---- partial matches: some files equal, some not -> report only, never delete
        cls_index = {d: i for i, c in enumerate(classes) for d in c}
        members = sorted(info)
        for i, a in enumerate(members):
            for b in members[i + 1:]:
                if a in cls_index and cls_index.get(b) == cls_index[a]:
                    continue                # fully identical, handled above
                if related(a, b):
                    continue
                matched, differing, only_a, only_b = compare_partial(info[a], info[b], args.ignore_filenames)
                if matched == 0:
                    continue
                partial += 1
                print("\nPARTIAL MATCH (reported only, nothing deleted)")
                print(f"  A: {a}  ({len(info[a])} files)")
                print(f"  B: {b}  ({len(info[b])} files)")
                print(f"  identical: {matched}, different content: {len(differing)}, "
                      f"only in A: {len(only_a)}, only in B: {len(only_b)}")
                if not differing and not only_a:
                    print("  -> A is a subset of B (every file of A exists identically in B)")
                elif not differing and not only_b:
                    print("  -> B is a subset of A (every file of B exists identically in A)")
                for label, items in (("different content", differing), ("only in A", only_a), ("only in B", only_b)):
                    if items:
                        print(f"  {label}: {fmt_list(items, args.max_list)}")

    print(f"\nDone: {found} identical set(s) found, {partial} partial match(es) (never deleted)"
          + (f", {deleted} director{'y' if deleted == 1 else 'ies'} deleted" if args.delete
             else " (report only, add --delete to remove older ones)"))


if __name__ == "__main__":
    main()
