#!/usr/bin/env bash
function usage {
    echo 'zip all (non compressed) files in the given folder\n'
    echo 'usage:' "$1" '-p <path/to/folder> [-b to break on error] [-z use 7z instead of zip] [-d to delete source files] [-m to move compressed files one folder up once generated] [-t to test run]'
}

_TEST_RUN=0
_BREAK_ON_ERROR=0
_DELETE_SRC=0
_USE_7Z=0
_MOVE_UP=0
while getopts "btzmdp:" arg; do
    case $arg in
        p)
          _PATH="${OPTARG}"
          ;;
        t)
          _TEST_RUN=1
          ;;
	m)
	  _MOVE_UP=1
	  ;;
        b)
          _BREAK_ON_ERROR=1
          ;;
        d)
          _DELETE_SRC=1
          ;;
        z)
          _USE_7Z=1
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

echo '[.] processing' "$_PATH"
find "$_PATH" -not -iname "*.zip" -not -iname "*.7z" > ./tmp2.txt
tail -n +2 ./tmp2.txt > ./tmp.txt
rm ./tmp2.txt

if [ $? -ne 0 ]; then
  echo '[x] wrong input, or no matches found!'
  rm ./tmp.txt
  exit 1
fi

while IFS= read -r line
do
  if [ -d "$line" ]; then
    continue
  fi

  _dodelete=0
  if [ $_TEST_RUN -eq 0 ]; then
    # no test
    _dodelete=1
  fi
  if [ $_DELETE_SRC -eq 0 ]; then
    # do not delete source file
    _dodelete=0
  fi

  # zip
  _barename=$(echo "$line" | rev | cut -c 5- | rev)
  _newfile="$_barename"
  if [ $_TEST_RUN -eq 0 ]; then
    # zip
    if [ $_USE_7Z == 0 ]; then
      echo "[.] compressing: $line to $_newfile.zip" 
      zip -D -j -q -9 "$_newfile.zip" "$line" 1>/dev/null
      if [ $_MOVE_UP -ne 0 ]; then
      	_dir=$(dirname "$_newfile.zip")
	echo "[.] moving $_newfile.zip to $_dir/../"
        mv "$_newfile.zip" "$_dir/../"
      fi
    else
      # use 7z
      echo "[.] compressing: $line to $_newfile.7z"
      7z a -y "$_newfile.7z" "$line" 1>/dev/null
      if [ $_MOVE_UP -ne 0 ]; then
        _dir=$(dirname "$_newfile.7z")
        echo "[.] moving $_newfile.7z to $_dir/../"
        mv "$_newfile.7z" "$_dir/../"
      fi
    fi

    if [ $? -ne 0 ]; then
      if [ $_BREAK_ON_ERROR -eq 1 ]; then
        exit 1
      fi
    fi
  fi

  if [ $_dodelete -ne 0 ]; then
    if [ $_TEST_RUN -eq 0 ]; then
      echo '[.] deleting:' "$line" 
      rm -f "$line"
    fi
  fi
done < "./tmp.txt"
rm ./tmp.txt

echo '[.] done!'

