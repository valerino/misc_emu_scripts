# 7z2zip

This script converts `.7z` archives to `.zip` format, preserving the original directory structure and file contents. It is designed to be used in batch mode, allowing you to process multiple archives in a specified directory.

### Features

| Option | Description |
|--------|-------------|
| `-p, --path` | **(Required)** Directory to scan for `.7z` files |
| `-d, --delete` | Delete the original `.7z` after successful conversion |
| `-t, --dry-run` | Print all operations without modifying any files |
| `-b, --break` | Stop execution immediately on the first error |

### Usage Examples

```bash
# Basic conversion (keeps originals)
7z2zip.py -p /path/to/archives

# Convert and delete originals
7z2zip.py -p /path/to/archives -d

# Preview what would happen without doing anything
7z2zip.py -p /path/to/archives -t

# Convert, delete originals, and stop on first error
7z2zip.py -p /path/to/archives -d -b

# Full dry-run with delete preview
7z2zip.py -p /path/to/archives -d -t -b
```

### What It Prints

For each `.7z` file found, the script prints:
- The current file being processed
- The extraction step (`un7zipping <file> -> <temp_dir>`)
- The 7z command output
- The compression step (`zipping <temp_dir> -> <file>.zip`)
- The zip command output
- Whether the original is being deleted
- Cleanup of the temporary directory
- A final summary of successes and failures

### Dependencies

Make sure `7z` (p7zip) and `zip` are installed and available in your `PATH`:
```bash
# Debian/Ubuntu
sudo apt-get install p7zip-full zip

# macOS
brew install p7zip zip

# Windows (with 7-Zip in PATH)
# Download from https://www.7-zip.org/
```