#!/usr/bin/env bash
_DEST_PATH=""
_SRC_PATH=""
_DELETE=0
_IGNORE_ERRORS=0
_WRKDIR="/tmp/_wrkdir"
_FILES="/tmp/_files"

function usage {
  echo 'convert zipped .CUE/BIN images to CHD.\n'
  echo 'usage:' "$1" '-p <path/to/dir_with_zipped_cuebin> -o </path/to/destination> [-d delete zips] [-i ignore errors]'
}

function cleanup {
    rm "$_FILES"
    rm -rf "$_WRKDIR"
}

while getopts "p:o:di" arg; do
  case $arg in
  p)
    _SRC_PATH=$(realpath "${OPTARG}")
    ;;
  o)
    _DEST_PATH=$(realpath "${OPTARG}")
    ;;
  d)
    _DELETE=1
    ;;
  i)
    _IGNORE_ERRORS=1
    ;;

  *)
    usage "$0"
    exit 1
    ;;
  esac
done

if [ -z "$_SRC_PATH" ] || [ -z "$_DEST_PATH" ]; then
  usage "$0"
  exit 1
fi

# get files list
_regex='.+(.zip|.ZIP)$'
find "$_SRC_PATH" | grep -E "$_regex" >"$_FILES"
if [ $? -ne 0 ]; then
    echo "no files in $_SRC_PATH !"
    cleanup
    exit 1
fi

# ensure destpath exists
mkdir -p "$_DEST_PATH"

# loop extract
while IFS= read -r _line; do
    echo '[.] extracting:' "$_line" 'to:' "$_WRKDIR"
    rm -rf "$_WRKDIR"
    mkdir -p "$_WRKDIR"
    unzip -o -d "$_WRKDIR" "$_line"
    if [ $? -ne 0 ]; then
        if [ "$_IGNORE_ERRORS" -eq 1 ]; then
            echo "ERROR!"
            cleanup
            exit 1
        fi
    fi
    
    # find cue file
    _regex='.+(.cue|.cue)$'
    _f=$(find "$_WRKDIR" | grep -E "$_regex")
    if [ "$?" -eq 0 ]; then
        # make chd
        _chd="${_f%%.*}.chd"
        chdman createcd -i "$_f" -o "$_chd"
        if [ "$?" -eq 0 ]; then
            # done, move to dest path
            cp "$_chd" "$_DEST_PATH"
            if [ "$?" -eq 0 ]; then
                _chd="${_line%%.*}.chd"
                echo "created $_chd !"
                if [ "$_DELETE" -eq 1 ]; then
                    echo "deleting $_line ..."
                    rm "$_line"
                fi
            fi
        fi
    fi

done < "$_FILES"
cleanup
