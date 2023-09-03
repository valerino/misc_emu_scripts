#!/usr/bin/env bash
_DEST_PATH=""
_SRC_PATH=""
_DELETE=0
_IGNORE_ERRORS=0
_WRKDIR="/tmp/_wrkdir"
_FILES="/tmp/_files"
_ZIPPED=0
_TESTRUN=0
_pwd=$(pwd)

function usage {
  echo 'convert .CUE/BIN images to CHD.\n'
  echo 'usage:' "$1" '-p <path/to/sourcedir> -o </path/to/destination> [-z sourcedir have zips] [-d delete zips/dirs] [-i to DO NOT ignore errors] [-t to testrun]'
}

function cleanup {
    rm "$_FILES"
    rm -rf "$_WRKDIR"
    cd "$_pwd"
}

while getopts "p:o:dizt" arg; do
  case $arg in
  z)
    _ZIPPED=1
    ;;
  t)
    _TESTRUN=1
    ;;
  p)
    _SRC_PATH=$(realpath "${OPTARG}")
    ;;
  o)
    mkdir -p "$OPTARG"
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

if [ "$_ZIPPED" -eq 1 ]; then
  # get files list
  _regex='.+(.zip)$'
  find "$_SRC_PATH" | grep -Ei "$_regex" >"$_FILES"
else
  # get dirs list
  find "$_SRC_PATH" -type d | sed "1d" >"$_FILES"
fi

if [ $? -ne 0 ]; then
    echo "no files/dirs in $_SRC_PATH !"
    cleanup
    exit 1
fi

# loop extract
while IFS= read -r _line; do
  if [ $_TESTRUN -eq 1 ]; then
    echo "[.] TEST extracting: $_line to: $_DEST_PATH ..."
    continue
  fi
  
  # ensure destpath exists
  mkdir -p "$_DEST_PATH"
  
  if [ "$_ZIPPED" -eq 1 ]; then
    # input are zips, extract
    echo "[.] extracting: $_line to: $_WRKDIR"
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
  else
    # input are already extracted directories
    cd "$_line"
    _WRKDIR="$_line"
    echo "[.] processing: $_WRKDIR"
  fi

  # find cue file
  _regex='.+(.cue)$'
  _f=$(find "$_WRKDIR" | grep -Ei "$_regex")
  if [ "$?" -eq 0 ]; then
    # make chd
    _chd_barename=$(basename "$_f" ".cue")
    _chd_path="$_DEST_PATH/$_chd_barename.chd"    
    chdman createcd -i "$_f" -o "$_chd_path"
    if [ "$?" -eq 0 ]; then
      # done
      echo "[.] created $_chd_path !"
      if [ "$_DELETE" -eq 1 ]; then
        echo "deleting $_line ..."
        if [ "$_ZIPPED" -eq 1 ]; then
          rm "$_line"
        else
          rm -rf "$_line"
        fi
      fi
    fi
  fi

done < "$_FILES"
cleanup
