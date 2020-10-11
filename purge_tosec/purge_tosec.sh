#!/usr/bin/env sh
function usage {
    echo 'purges the given TOSEC set from a,b,o,v,u,m,h dumps.\n'
    echo 'usage:' "$1" '-p <path/to/folder [-t to test run, no deletion] [-h to keep hacks/modified]'
    echo '\t[-a to keep alternates] [-b to force delete [b] anyway]'
    echo '\nNOTE:\n'
    echo 'Before deleting, the script makes sure to delete a file ONLY if at least a "good" copy is kept, either it will keep the "bad".'
    echo 'The only exception is for [b] dumps with the -b option specified (thus, force deletes the only copy which is "bad").'
}

_KEEP_HACKS=0
_KEEP_ALTS=0
_TEST_RUN=0
_FORCE_DELETE_BADS=0
while getopts "habtp:" arg; do
    case $arg in
        p)
          _PATH="${OPTARG}"
          ;;
        h) 
          _KEEP_HACKS=1
          ;;
        b) 
          _FORCE_DELETE_BADS=1
          ;;
        a)
          _KEEP_ALTS=1
          ;;
        t)
          _TEST_RUN=1
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

_regex='\[(b|o|v|u'
if [ $_KEEP_ALTS -eq 0 ]; then
  _regex="$_regex"'|a'
else
  echo '[w] keeping alternates'
fi

if [ $_FORCE_DELETE_BADS -eq 1 ]; then
  echo '[w] forcing deletion of [b]'
fi

if [ $_KEEP_HACKS -eq 0 ]; then
  _regex="$_regex"'|h|m'
else
  echo '[w] keeping hacks'
fi

if [ $_TEST_RUN -eq 1 ]; then
  echo '[w] TEST RUN (no deletion will happen)'
fi

echo '[.] processing' "$_PATH"
_regex="$_regex"')(\d*)(\s.+){0,1}]'
find "$_PATH" | grep -E "$_regex" > ./tmp.txt
if [ $? -ne 0 ]; then
  echo '[x] wrong input, or no matches found!'
  rm ./tmp.txt
  exit 1
fi

echo '[.] using regex:' "$_regex"
while IFS= read -r line
do
  # default is to keep
  _dodelete=0

  # check if this is the only entry for basename
  _base=$(echo "$line" | cut -d [ -f1)
  _copies=$(ls -l "$_base"* | wc -l) 
  if [ "$_copies" -gt 1 ]; then
    if [ $_TEST_RUN -eq 0 ]; then
      # mark for deletion
      _dodelete=1
    fi  
  else
    # there's a single copy of this file, check for [b] and _FORCE_DELETE_BADS
    echo '[w] SINGLE COPY:' "$line"
    _isbad=$(echo "$line" | grep '\[b]')
    if [ "$_isbad" != "" ]; then
      if [ $_FORCE_DELETE_BADS -eq 1 ]; then
        # mark for deletion
        if [ $_TEST_RUN -eq 0 ]; then
          # mark for deletion
          _dodelete=1
        fi  
        echo '[w] SINGLE COPY, FORCE DELETE' "$_isbad"
      fi
    fi      
  fi

  # delete ?
  if [ "$_dodelete" -eq 1 ]; then
    echo '[.] deleting' "$line"
    rm -f "$line"
  else
    echo '[.] deleting (TEST)' "$line"
  fi


done < "./tmp.txt"
rm ./tmp.txt

echo '[.] done!'
