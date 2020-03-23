#!/usr/bin/env sh
function usage {
    echo 'unzip all files in the given folder\n'
    echo 'usage:' "$0" '-p <path/to/folder> [-b to break on error] [-z use 7z instead of unzip] [-d to delete source zips] [-t to test run]'
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
    echo '[.] extracting:' "$line" 'to:' "$_destdir"
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

    if [ $_dodelete -ne 0 ]; then
      rm -f "$line"
    fi
  fi
done < "./tmp.txt"
rm ./tmp.txt

echo '[.] done!'

