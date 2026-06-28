#!/bin/bash

show_help() {
    cat << 'EOF'
Usage: delete_files_recursive.sh [OPTIONS] <directory>

Delete all files recursively while preserving directory structure.

Options:
  --dry-run    Preview files that would be deleted without actually deleting them.
               Prints the full path of each file.
  --help       Display this help message and exit.

Examples:
  ./delete_files_recursive.sh /path/to/directory
  ./delete_files_recursive.sh --dry-run /path/to/directory
  ./delete_files_recursive.sh --help
EOF
}

# Parse arguments
DRY_RUN=false
TARGET_DIR=""

for arg in "$@"; do
    if [ "$arg" = "--help" ]; then
        show_help
        exit 0
    elif [ "$arg" = "--dry-run" ]; then
        DRY_RUN=true
    elif [ -z "$TARGET_DIR" ]; then
        TARGET_DIR="$arg"
    fi
done

if [ -z "$TARGET_DIR" ]; then
    echo "Error: No directory specified."
    echo ""
    show_help
    exit 1
fi

if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: '$TARGET_DIR' is not a valid directory."
    exit 1
fi

if [ "$DRY_RUN" = true ]; then
    echo "=== DRY RUN MODE - No files will be deleted ==="
    find "$TARGET_DIR" -type f -print
    echo "=== End of dry run ==="
else
    find "$TARGET_DIR" -type f -exec rm -f -- {} +
    echo "All files deleted from '$TARGET_DIR' and its subdirectories."
fi
