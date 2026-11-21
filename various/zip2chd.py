#!/usr/bin/env python3
"""Convert a .zip containing a .cue/.bin disc image into a .chd using chdman."""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def find_cue(root: Path) -> Path:
    cues = sorted(
        p for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() == ".cue" and not p.name.startswith(".")
    )
    if not cues:
        raise FileNotFoundError("no .cue file found in the archive")
    if len(cues) > 1:
        print(f"warning: {len(cues)} .cue files found, using {cues[0].name}", file=sys.stderr)
    return cues[0]


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract a zip, find its .cue and create a .chd with chdman.")
    ap.add_argument("--in", dest="zipfile", required=True, help="input .zip file")
    ap.add_argument("--out", dest="chdfile", help="output .chd file (default: input name with .chd extension)")
    ap.add_argument("--delete", action="store_true", help="delete the input zip after a successful conversion")
    ap.add_argument("--chdman", default="chdman", help="path to the chdman executable (default: chdman)")
    args = ap.parse_args()

    zip_path = Path(args.zipfile).resolve()
    if not zip_path.is_file():
        ap.error(f"input file not found: {zip_path}")

    chd_path = Path(args.chdfile).resolve() if args.chdfile else zip_path.with_suffix(".chd")
    if chd_path.exists():
        ap.error(f"output file already exists: {chd_path}")

    if shutil.which(args.chdman) is None:
        ap.error(f"chdman executable not found: {args.chdman}")

    origin = Path.cwd()
    try:
        # TemporaryDirectory is always removed on exit, even on errors
        with tempfile.TemporaryDirectory(prefix="zip2chd_") as tmp:
            tmp_dir = Path(tmp)
            print(f"Extracting {zip_path.name} ...")
            with zipfile.ZipFile(zip_path) as zf:
                zf.extractall(tmp_dir)

            cue = find_cue(tmp_dir)
            os.chdir(cue.parent)  # cue sheets reference their .bin files relatively

            cmd = [args.chdman, "createcd", "-i", cue.name, "-o", str(chd_path)]
            print("Running:", " ".join(cmd))
            try:
                result = subprocess.run(cmd)
            finally:
                os.chdir(origin)  # leave the temp dir so it can be deleted (required on Windows)

            if result.returncode != 0:
                chd_path.unlink(missing_ok=True)  # drop partial output
                print(f"chdman failed with exit code {result.returncode}", file=sys.stderr)
                return result.returncode
    except (zipfile.BadZipFile, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    finally:
        os.chdir(origin)

    print(f"Created {chd_path}")
    if args.delete:
        zip_path.unlink()
        print(f"Deleted {zip_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
