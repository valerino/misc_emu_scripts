#!/usr/bin/env bash
function usage {
    echo 'zip all (non compressed) files in the given folder\n'
    echo 'usage:' "$1" '-p <path/to/folder> [-b to break on error] [-z use 7z instead of zip] [-d to delete source files] [-m to move compressed files one folder up once generated] [-s to delete the containing folder after moving, to be used with -m] [-t to test run] [-i <default|csv> ignore extensions: default ignores common companion files, or specify a csv list like .txt,.md,.png] [-a <csv> add only files with these extensions (case-insensitive csv list like .txt,.md,.png,...)]'
}

_TEST_RUN=0
_BREAK_ON_ERROR=0
_DELETE_SRC=0
_USE_7Z=0
_MOVE_UP=0
_DEL_AFTER_MOVE=0
_IGNORE_COMPANION=0
_IGNORE_COMPANION_DEFAULT=0
_IGNORE_COMPANION_EXTENSIONS=""
_ONLY_EXTENSIONS=""
_ALLOWED_EXTENSIONS=""

while getopts "btzmdsp:i:a:" arg; do
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
        i)
          _IGNORE_COMPANION=1
          if [ "${OPTARG}" == "default" ]; then
            _IGNORE_COMPANION_DEFAULT=1
          else
            _IGNORE_COMPANION_EXTENSIONS="${OPTARG}"
          fi
          ;;
        s)
      	  _DEL_AFTER_MOVE=1
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
        a)
          _ONLY_EXTENSIONS="${OPTARG}"
          ;;
        *)
          usage "$0"
          exit 1
          ;;
    esac
done

if [ "$_IGNORE_COMPANION_EXTENSIONS" != "" ]; then
  _IGNORE_COMPANION_EXTENSIONS=$(echo "$_IGNORE_COMPANION_EXTENSIONS" | tr '[:upper:]' '[:lower:]' | tr ',' '\n' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//' | sed 's/^\.//' | tr '\n' ' ')
fi

if [ "$_ONLY_EXTENSIONS" != "" ]; then
  _ALLOWED_EXTENSIONS=$(echo "$_ONLY_EXTENSIONS" | tr '[:upper:]' '[:lower:]' | tr ',' '\n' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//' | sed 's/^\.//' | tr '\n' ' ')
fi

if [ "$_PATH" == "" ]; then
  usage "$0"
  exit 1
fi

echo '[.] processing' "$_PATH"
find "$_PATH" -not -iname "*.zip" -not -iname "*.7z" > /tmp/tmp2.txt
tail -n +2 /tmp/tmp2.txt > /tmp/tmp.txt
rm /tmp/tmp2.txt

if [ $? -ne 0 ]; then
  echo '[x] wrong input, or no matches found!'
  rm /tmp.txt
  exit 1
fi

while IFS= read -r line
do
  if [ -d "$line" ]; then
    continue
  fi

  _basename=$(basename "$line")
  _basename_lower=$(echo "$_basename" | tr '[:upper:]' '[:lower:]')
  _ext=${_basename_lower##*.}

  if [ "$_ONLY_EXTENSIONS" != "" ]; then
    _match=0
    for _allowed in $_ALLOWED_EXTENSIONS; do
      if [ -z "$_allowed" ]; then
        continue
      fi
      if [[ "$_basename_lower" == *".$_allowed" ]]; then
        _match=1
        break
      fi
    done
    if [ $_match -eq 0 ]; then
      echo "[.] skipping file with extension .$_ext: $line"
      continue
    fi
  fi

  # filter files if -i is specified
  if [ $_IGNORE_COMPANION -eq 1 ]; then
    if [ $_IGNORE_COMPANION_DEFAULT -eq 1 ]; then
      if [[ "$_basename_lower" == *.txt ]] || [[ "$_basename_lower" == *.md ]] || [[ "$_basename_lower" == *.png ]] || [[ "$_basename_lower" == *.gif ]] || [[ "$_basename_lower" == *.jpg ]] || [[ "$_basename_lower" == *.jpeg ]] || [[ "$_basename_lower" == *.pdf ]] || [[ "$_basename_lower" == *.doc ]] || [[ "$_basename_lower" == *.docx ]] || [[ "$_basename_lower" == *.rtf ]] || [[ "$_basename_lower" == *.pcm ]] || [[ "$_basename_lower" == *.wav ]] || [[ "$_basename_lower" == *.mp3 ]] || [[ "$_basename_lower" == *.mp4 ]] || [[ "$_basename_lower" == *.zip ]] || [[ "$_basename_lower" == *.rar ]] || [[ "$_basename_lower" == *.7z ]]; then
        echo "[.] ignoring companion file: $line"
        continue
      fi
    else
      _ignore_match=0
      for _allowed in $_IGNORE_COMPANION_EXTENSIONS; do
        if [ -z "$_allowed" ]; then
          continue
        fi
        if [[ "$_basename_lower" == *".$_allowed" ]]; then
          _ignore_match=1
          break
        fi
      done
      if [ $_ignore_match -eq 1 ]; then
        echo "[.] ignoring listed companion file: $line"
        continue
      fi
    fi
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
  _newfile="$line"

  if [ $_TEST_RUN -eq 0 ]; then
    # zip
    if [ $_USE_7Z == 0 ]; then
      echo "[.] compressing: $line to $_newfile.zip" 
      zip -D -j -q -9 "$_newfile.zip" "$line" 1>/dev/null
      if [ $_MOVE_UP -ne 0 ]; then
      	_dir=$(dirname "$_newfile.zip")
	echo "[.] moving $_newfile.zip to $_dir/../"
        mv "$_newfile.zip" "$_dir/../"
	if [ $_DEL_AFTER_MOVE -eq 1 ]; then
	  echo "[.] deleting folder $_dir"
	  rm -rf "$_dir"
	fi
      fi
    else
      # use 7z
      echo "[.] compressing: $line to $_newfile.7z"
      7z a -y "$_newfile.7z" "$line" 1>/dev/null
      if [ $_MOVE_UP -ne 0 ]; then
        _dir=$(dirname "$_newfile.7z")
        echo "[.] moving $_newfile.7z to $_dir/../"
        mv "$_newfile.7z" "$_dir/../"
        if [ $_DEL_AFTER_MOVE -eq 1 ]; then
          echo "[.] deleting folder $_dir"
          rm -rf "$_dir"
        fi
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
done < "/tmp/tmp.txt"
rm /tmp/tmp.txt

echo '[.] done!'

