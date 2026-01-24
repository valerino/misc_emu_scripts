iso_to_rvz
=========

Converts .iso files (or archives containing a single or multiple .iso files) to .rvz using `dolphin-tool`.

Usage
-----

Basic:

    ./iso_to_rvz.sh -p <path/to/folder|path/to/file>

Options:

- `-p <path>` : directory to scan or a single file to process (required; supports `.iso`, `.zip`, `.7z`)
- `-o <output>` : output directory for .rvz files (defaults to the input path)
- `-t` : test run (no writes, prints what it would do; archives are listed instead of extracted)
- `-d` : delete source files after successful conversion
- `-z` : use `7z` for extraction (default is `unzip`)
- `-s` : enable `dolphin-tool`'s `--scrub` option to remove junk data during conversion (adds `-s` to the convert command)
- `-f <format>` : output container format. Supported values: `rvz` (default), `gcz`, `wia`, `iso`
- `-l <level>` : compression level for the selected method (default: 5). Valid integer range: 0-22. Recommended value for zstd: 5.

Behavior
--------

- Scans the specified folder (or single file) for `.iso`, `.zip` and `.7z` files.
- If a file is an archive it extracts any `.iso` files to a temporary directory, converts each `.iso` to `.rvz` with `dolphin-tool`, then removes extracted `.iso` files.
- In test mode (`-t`), archives are not extracted; instead the script lists `.iso` entries found inside the archive (using `7z` or `unzip`) and prints which conversions would be performed.
- If `-d` is specified, the script will only delete the source archive if *all* its extracted `.iso` conversions succeed; for standalone `.iso` files, they can be removed after a successful conversion.
- The script verifies `dolphin-tool` and the chosen extraction tool (`unzip` or `7z`) are available and will abort with a clear error if missing.

Examples
--------

- Dry run (print actions, no writes):

    ./iso_to_rvz.sh -p /path/to/input -t

- Convert and delete source archives on success, using 7z for extraction:

    ./iso_to_rvz.sh -p /path/to/input -d -z

Test script
-----------

A basic test script `test_iso_to_rvz.sh` is provided that performs a minimal smoke test using the script's test mode (`-t`). The test doesn't require `dolphin-tool` to be present because it uses test mode.

Notes
-----

- `dolphin-tool` is expected to be in PATH. The script uses the `convert` subcommand with recommended RVZ options:

    dolphin-tool convert -i <input.iso> -o <output.rvz> -f rvz -b 131072 -c zstd -l 5

  If your `dolphin-tool` requires different flags or you want other defaults, tell me and I can add a `-c/--convert-cmd` option to customize the invocation.
