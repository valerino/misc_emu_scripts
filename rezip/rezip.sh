#!/usr/bin/env bash
function usage {
  echo 'rezip files in the given zip.\n'
  echo 'usage:' "$1" '-p <path/to/src_zip> [-o destination zip|destination dir (source path basename will be used), default is to overwrite source zip] [-z to unzip individual files and delete the zips] [-i to ignore unzip errors]'
}

_DEST_PATH=""
_IGNORE_ERRORS=0
_UNZIP_INDIVIDUAL=0
while getopts "o:p:iz" arg; do
  case $arg in
  p)
    _PATH=$(realpath "${OPTARG}")
    _DEST_PATH=$(realpath "${OPTARG}")
    ;;
  o)
    _DEST_PATH=$(realpath "${OPTARG}")
    ;;
  z)
    _UNZIP_INDIVIDUAL=1
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

if [ "$_PATH" == "" ]; then
  usage "$0"
  exit 1
fi

if [ -d "$_DEST_PATH" ]; then
  # extract basename from path and use it in the destpath
  _f=$(basename "$_PATH")
  _DEST_PATH="$_DEST_PATH/$_f"
fi

echo '[.] unzipping' "$_PATH"
_tmpunz=$(realpath "./tmpunz")
mkdir -p "$_tmpunz"
unzip -j -o -d "$_tmpunz" "$_PATH" 1>/dev/null
if [ $? -ne 0 ]; then
  if [ "$_IGNORE_ERRORS" -eq 0 ]; then
    rm -rf "$_tmpunz"
    exit 1
  fi
fi

if [ "$_UNZIP_INDIVIDUAL" -eq 1 ]; then
  # unzip individual zips too
  _regex='.+(.zip|.ZIP)$'
  find "$_tmpunz" | grep -E "$_regex" >./tmp.txt
  if [ $? -eq 0 ]; then
    while IFS= read -r line; do
      # unzip and remove zip
      echo '[.] extracting:' "$line" 'to:' "$_tmpunz"
      unzip -o -d "$_tmpunz" "$line" 1>/dev/null
      if [ $? -ne 0 ]; then
        if [ "$_IGNORE_ERRORS" -eq 0 ]; then
          rm -rf "$_tmpunz"
          rm ./tmp.txt
          exit 1
        fi
      fi
      rm -f "$line"
    done <"./tmp.txt"
  fi
  rm ./tmp.txt
fi

echo "[.] rezipping $_PATH to $_DEST_PATH"
_tmpzip=$(realpath "./tmpzip.zip")
_PWD=$(pwd)
cd "$_tmpunz"
zip -9 -r "$_tmpzip" .
if [ $? -ne 0 ]; then
  cd $_PWD
  rm -rf "$_tmpunz"
  exit 1
fi
cd $_PWD
cp "$_tmpzip" "$_DEST_PATH"
rm "$_tmpzip"
rm -rf "$_tmpunz"

echo "[.] done, created $_DEST_PATH !"
