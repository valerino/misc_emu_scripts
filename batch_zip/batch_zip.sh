#!/usr/bin/env sh
function usage {
    echo 'zip all (non compressed) files in the given folder\n'
    echo 'usage:' "$1" '-p <path/to/folder> [-b to break on error] [-z use 7z instead of zip] [-d to delete source files] [-t to test run]'
}

_TEST_RUN=0
_BREAK_ON_ERROR=0
_DELETE_SRC=0
_USE_7Z=0
while getopts "btzdp:" arg; do
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
  _dodelete=0
  if [ $_TEST_RUN -eq 0 ]; then
    # no test
    _dodelete=1
  fi
	if [ $_DELETE_SRC -eq 0 ]; then
	  # do not delete source zip
	  _dodelete=0
	fi

  if [ $_TEST_RUN -eq 0 ]; then
    # unzip
    _destdir=$_PATH
    _barename=$(echo "$line" | rev | cut -c 5- | rev)
    _newfile="$_barename"
    echo '[.] compressing:' "$line" 'to:' "$_newfile"
    if [ $_USE_7Z == 0 ]; then
      zip -D -j -q -9 "$_newfile".zip "$line" 1>/dev/null
    else
      # use 7z
      7z a -y "$_newfile".7z "$line" 1>/dev/null
    fi

    if [ $? -ne 0 ]; then
      if [ $_BREAK_ON_ERROR -eq 1 ]; then
        exit 1
      fi
    fi

    if [ $_dodelete -ne 0 ]; then
      rm -f "$line"
    fi
  fi
done < "./tmp.txt"
rm ./tmp.txt

echo '[.] done!'

