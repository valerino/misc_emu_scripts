#!/usr/bin/env python3
"""
7z to Zip converter script.

Usage:
    python convert_7z_to_zip.py -p <directory> [-d] [-t] [-b]

Options:
    -p, --path      Directory to scan for .7z files
    -d, --delete    Delete original .7z files after conversion
    -t, --dry-run   Print operations without modifying files
    -b, --break     Stop on first error
"""

import argparse
import os
import subprocess
import sys
import tempfile
import shutil


def run_command(cmd, description, dry_run=False, break_on_error=False):
    """Run a shell command and handle errors."""
    print(f"  [CMD] {description}")
    print(f"        {' '.join(cmd)}")

    if dry_run:
        print("  [DRY-RUN] Command would execute here")
        return True

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                print(f"        {line}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Command failed with exit code {e.returncode}")
        if e.stdout:
            for line in e.stdout.strip().split('\n'):
                print(f"        OUT: {line}")
        if e.stderr:
            for line in e.stderr.strip().split('\n'):
                print(f"        ERR: {line}")
        if break_on_error:
            print("  [BREAK] Stopping due to --break-on-error")
            sys.exit(1)
        return False
    except FileNotFoundError:
        print(f"  [ERROR] Command not found: {cmd[0]}")
        print("          Make sure '7z' and 'zip' are installed and in PATH")
        if break_on_error:
            sys.exit(1)
        return False


def find_7z_files(directory):
    """Find all .7z files in the given directory (non-recursive)."""
    files = []
    try:
        for entry in os.listdir(directory):
            if entry.lower().endswith('.7z'):
                full_path = os.path.join(directory, entry)
                if os.path.isfile(full_path):
                    files.append(full_path)
    except OSError as e:
        print(f"[ERROR] Cannot read directory '{directory}': {e}")
        sys.exit(1)
    return sorted(files)


def convert_7z_to_zip(archive_path, delete_original=False, dry_run=False, break_on_error=False):
    """Convert a single .7z file to .zip."""
    directory = os.path.dirname(os.path.abspath(archive_path))
    basename = os.path.basename(archive_path)
    name_without_ext = os.path.splitext(basename)[0]
    zip_filename = f"{name_without_ext}.zip"
    zip_path = os.path.join(directory, zip_filename)

    print(f"\n{'='*60}")
    print(f"[PROCESSING] {basename}")
    print(f"  Source:      {archive_path}")
    print(f"  Target:      {zip_path}")
    print(f"  Delete orig: {delete_original}")
    print(f"  Dry run:     {dry_run}")

    # Check if zip already exists
    if os.path.exists(zip_path):
        print(f"  [WARNING] Target already exists: {zip_path}")
        if break_on_error:
            print("  [BREAK] Stopping due to --break-on-error")
            sys.exit(1)
        print("  [SKIP] Skipping this file")
        return False

    # Create temporary directory for extraction
    if dry_run:
        temp_dir = f"<temp_dir_for_{name_without_ext}>"
        print(f"  [DRY-RUN] Would create temp directory: {temp_dir}")
    else:
        temp_dir = tempfile.mkdtemp(prefix=f"7z2zip_{name_without_ext}_")
        print(f"  [TEMP] Created: {temp_dir}")

    try:
        # Step 1: Extract 7z to temp directory
        print(f"\n  [STEP 1] Extracting 7z archive...")
        print(f"           un7zipping '{basename}' -> '{temp_dir}'")

        extract_cmd = ['7z', 'x', archive_path, f'-o{temp_dir}', '-y']
        if not run_command(extract_cmd, f"Extract {basename}", dry_run, break_on_error):
            return False

        # Step 2: Zip the extracted content
        print(f"\n  [STEP 2] Creating zip archive...")
        print(f"           zipping '{temp_dir}' -> '{zip_filename}'")

        # Use -r for recursive and handle empty directories gracefully
        zip_cmd = ['zip', '-r', zip_path, '.']

        if dry_run:
            if not run_command(zip_cmd, f"Create {zip_filename}", dry_run=True, break_on_error=break_on_error):
                return False
        else:
            # Change to temp dir so zip contents are relative
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            try:
                if not run_command(zip_cmd, f"Create {zip_filename}", dry_run=False, break_on_error=break_on_error):
                    os.chdir(original_cwd)
                    return False
            finally:
                os.chdir(original_cwd)

        # Step 3: Optionally delete original
        if delete_original:
            print(f"\n  [STEP 3] Deleting original 7z file...")
            print(f"           removing '{archive_path}'")
            if dry_run:
                print(f"  [DRY-RUN] Would delete: {archive_path}")
            else:
                try:
                    os.remove(archive_path)
                    print(f"  [OK] Deleted: {archive_path}")
                except OSError as e:
                    print(f"  [ERROR] Failed to delete {archive_path}: {e}")
                    if break_on_error:
                        sys.exit(1)
                    return False

        print(f"\n  [SUCCESS] Converted: {basename} -> {zip_filename}")
        return True

    finally:
        # Cleanup temp directory
        if not dry_run and os.path.exists(temp_dir):
            print(f"\n  [CLEANUP] Removing temp directory: {temp_dir}")
            try:
                shutil.rmtree(temp_dir)
                print(f"  [OK] Temp directory removed")
            except OSError as e:
                print(f"  [WARNING] Failed to remove temp directory: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Convert .7z archives to .zip format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -p /path/to/archives
  %(prog)s -p /path/to/archives -d
  %(prog)s -p /path/to/archives -t
  %(prog)s -p /path/to/archives -d -t -b
        """
    )
    parser.add_argument(
        '-p', '--path',
        required=True,
        help='Directory containing .7z files to convert'
    )
    parser.add_argument(
        '-d', '--delete',
        action='store_true',
        help='Delete original .7z files after successful conversion'
    )
    parser.add_argument(
        '-t', '--dry-run',
        action='store_true',
        help='Print operations without modifying any files'
    )
    parser.add_argument(
        '-b', '--break',
        dest='break_on_error',
        action='store_true',
        help='Stop processing on first error'
    )

    args = parser.parse_args()

    target_dir = os.path.abspath(args.path)

    print(f"{'='*60}")
    print(f"7z to Zip Converter")
    print(f"{'='*60}")
    print(f"Directory:   {target_dir}")
    print(f"Delete orig: {args.delete}")
    print(f"Dry run:     {args.dry_run}")
    print(f"Break:       {args.break_on_error}")

    if not os.path.isdir(target_dir):
        print(f"\n[ERROR] Not a directory: {target_dir}")
        sys.exit(1)

    archives = find_7z_files(target_dir)

    if not archives:
        print(f"\n[INFO] No .7z files found in: {target_dir}")
        sys.exit(0)

    print(f"\nFound {len(archives)} .7z file(s):")
    for i, arc in enumerate(archives, 1):
        print(f"  {i}. {os.path.basename(arc)}")

    success_count = 0
    fail_count = 0

    for archive in archives:
        if convert_7z_to_zip(
            archive,
            delete_original=args.delete,
            dry_run=args.dry_run,
            break_on_error=args.break_on_error
        ):
            success_count += 1
        else:
            fail_count += 1
            if args.break_on_error:
                break

    print(f"\n{'='*60}")
    print(f"[SUMMARY]")
    print(f"  Total:   {len(archives)}")
    print(f"  Success: {success_count}")
    print(f"  Failed:  {fail_count}")
    print(f"{'='*60}")

    if fail_count > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
    