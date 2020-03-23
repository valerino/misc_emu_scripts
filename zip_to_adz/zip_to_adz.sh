#!/usr/bin/env sh
function usage {
    echo 'turn all zipped .ADF in the given folder to .ADZ\n'
    echo 'usage:' "$0" '-p <path/to/folder> [-b to break on error] [-z use 7z instead of unzip] [-t to test run, no deletion of source .ZIPs]'
}

_TEST_RUN=0
_BREAK_ON_ERROR=0
_USE_7Z=0
while getopts "btzp:" arg; do
    case $arg in
        p)
          _PATH="${OPTARG}"
          ;;
        t)
          _TEST_RUN=1
          ;;
        b)
          _BREAK_ON_ERROR=1
          ;;
        z)
          _USE_7Z=1
          ;;
        *)
          usage
          exit 1
          ;;
    esac
done

if [ "$_PATH" == "" ]; then
  usage
  exit 1
fi

echo '[.] processing' "$_PATH"
_regex='.+(.zip|.ZIP)$'
find "$_PATH" | grep -E "$_regex" > ./tmp.txt
if [ $? -ne 0 ]; then
  echo '[x] wrong input, or no matches found!'
  rm ./tmp.txt
  exit 1
fi

while IFS= read -r line
do
  _dodelete=0
  _domove=0
  if [ $_TEST_RUN -eq 0 ]; then
    # no test
    _dodelete=1
    _domove=1
  fi

  # unzip to tmp
  echo '[.] extracting:' "$line"
  _destdir=/tmp/unz
  rm -rf "$_destdir"
  mkdir -p "$_destdir"
  if [ $_USE_7Z == 0 ]; then
    unzip -o -d "$_destdir" "$line" 1>/dev/null
  else
    # use 7z
    7z x -y -o"$_destdir" "$line" 1>/dev/null
  fi
  if [ $? -ne 0 ]; then
    if [ $_BREAK_ON_ERROR -eq 1 ]; then
      exit 1
    fi
  fi

  # recompress
  _barename=$(echo "$line" | rev | cut -c 5- | rev)
  _newfile="$_barename".adf.adz
  gzip --best --suffix .adz "$_destdir"/*
  if [ $? -ne 0 ]; then
    if [ $_BREAK_ON_ERROR -eq 1 ]; then
      exit 1
    fi
  fi

  if [ $_TEST_RUN -eq 0 ]; then
    echo '[.] generating:' "$_newfile"
    mv "$_destdir"/* "$_newfile"
    if [ $? -ne 0 ]; then
      if [ $_BREAK_ON_ERROR -eq 1 ]; then
        exit 1
      fi
    fi
  else
      echo '[.] generating (TEST_RUN):' "$_newfile"
  fi

  if [ $_TEST_RUN -eq 0 ]; then
    rm -f "$line"
  fi
done < "./tmp.txt"
rm ./tmp.txt
rm -rf "$_destdir"

echo '[.] done!'
