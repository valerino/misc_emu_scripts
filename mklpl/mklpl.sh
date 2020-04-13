#!/usr/bin/env sh

function usage {
    echo 'generates retroarch (> 1.7.6, json) .LPL playlist\n'
    echo 'usage:' "$1" '-p <path/to/folder_to_scan> <-s path/to/parent/folder_on_destination_machine> -d </path/to/playlist>'
    echo '\t<-c /path/to/core_on_destination_machine> <-n core_name> [-z to strip further extension from labels (i.e. for .adf.adz files)]'
    echo '\t[-l label_display_mode, default 0] [-r right_thumbnail_mode, default 0] [-t left_thumbnail_mode, default 0]'
    echo '\t[-x /path/to/merge file to use in another invocation] [-y input merge file previously generated with -x]\n'
    echo 'path specified with -s must be the parent path on the destination machine where folder_to_scan is.\n'
    echo 'if -x is specified, merge_file is generated and can be specified with -y to generate another merged playlist.'
    echo 'NOTE: to be sorted correctly, both the paths in merge_file generated with -x and the -p path in the new invocation must have the same depth!\n'
    echo 'when -x is specified, every other parameters are ignoted except -p and -y.'
    echo 'if both -x and -y are specified, merge_file is read in input, merged with the content of the path at -p and rewritten.'
}

_LABEL_DISPLAY_MODE=0
_RIGHT_THUMBNAIL_MODE=0
_LEFT_THUMBNAIL_MODE=0
_GENERATE_MERGE=0
_MERGE_IN_PATH=""
_MERGE_OUT_PATH=""
_STRIP_FURTHER=0
while getopts "p:d:s:c:n:l:r:t:y:x:z" arg; do
    case $arg in
        p)
          _PATH="${OPTARG}"
          ;;
        z)
          _STRIP_FURTHER=1
          ;;
        y)
          _MERGE_IN_PATH="${OPTARG}"
          ;;
        x)
          _MERGE_OUT_PATH="${OPTARG}"
          ;;
        s)
          _PATH_DEST="${OPTARG}"
          ;;
        d)
          _LPL_PATH="${OPTARG}"
          ;;
        c)
          _CORE_PATH="${OPTARG}"
          ;;
        n)
          _CORE_NAME="${OPTARG}"
          ;;
        l)
          _LABEL_DISPLAY_MODE="${OPTARG}"
          ;;
        r)
          _RIGHT_THUMBNAIL_MODE="${OPTARG}"
          ;;
        t)
          _LEFT_THUMBNAIL_MODE="${OPTARG}"
          ;;
        *)
          usage "$0"
          exit 1
          ;;
    esac
done

if [ ! -z "$_MERGE_IN_PATH" ] || [ ! -z "$_MERGE_OUT_PATH" ]; then
  if [ "$_PATH" == "" ]; then
    usage "$0"
    exit 1
  fi
else
  if [ "$_PATH" == "" ] || [ "$_PATH_DEST" == "" ] || [ "$_LPL_PATH" == "" ] || [ "$_CORE_PATH" == "" ] || [ "$_CORE_NAME" == "" ]; then
    usage "$0"
    exit 1
  fi
fi

# get all files
find "$_PATH" > ./tmp.txt
if [ ! -z "$_MERGE_IN_PATH" ]; then
    echo '[.] adding merge file' "$_MERGE_IN_PATH"
    cat "$_MERGE_IN_PATH" >> ./tmp.txt
fi

# sort list
_countdelim=$(echo "$_PATH" | grep -o '/' | wc -l)
(( _countdelim+=2 ))
tail -n +2 ./tmp.txt > tmp2.txt
rm ./tmp.txt
sort -f -t'/' -k $_countdelim ./tmp2.txt > tmp.txt
rm ./tmp2.txt

if [ ! -z "$_MERGE_OUT_PATH" ]; then
  echo '[.] generated merge file in' "$_MERGE_OUT_PATH"
  mv ./tmp.txt "$_MERGE_OUT_PATH"
  exit 0
fi

echo '[.] generating' "$_LPL_PATH"
rm -f "$_LPL_PATH"

# generate header
echo '{' >> "$_LPL_PATH"
echo '\t"version": "1.2",' >> "$_LPL_PATH"
echo '\t"default_core_path":' \""$_CORE_PATH"\", >> "$_LPL_PATH"
echo '\t"default_core_name":' \""$_CORE_NAME"\", >> "$_LPL_PATH"
echo '\t"label_display_mode":' "$_LABEL_DISPLAY_MODE", >> "$_LPL_PATH"
echo '\t"right_thumbnail_mode":' "$_RIGHT_THUMBNAIL_MODE", >> "$_LPL_PATH"
echo '\t"left_thumbnail_mode":' "$_LEFT_THUMBNAIL_MODE", >> "$_LPL_PATH"
echo '\t"items": [' >> "$_LPL_PATH"

_count=0
while IFS= read -r line
do
  # init json
  if [ $_count -eq 0 ]; then
    echo '\t\t{' >> "$_LPL_PATH"
  else
    echo '\t\t,{' >> "$_LPL_PATH"
  fi

  # add filepath
  _tmpdd=$(dirname "$line")
  _tmpd=$(basename "$_tmpdd")
  _tmpn=$(basename "$line")
  _tmp="$_PATH_DEST"/"$_tmpd"/"$_tmpn"
  echo '\t\t\t"path":' \""$_tmp"\", >> "$_LPL_PATH"

  # get filename without extension
  _tmp=$(basename "$line")
  _name=$(echo "$_tmp" | rev | cut -c 5- | rev)

  # generate entry
  if [ $_STRIP_FURTHER -eq 1 ]; then
    # strip extension further
    _tmp="$_name"
    _name=$(echo "$_tmp" | rev | cut -c 5- | rev)
  fi

  echo '[.] adding' "$_name"
  echo '\t\t\t"label":' \""$_name"\", >> "$_LPL_PATH"
  echo '\t\t\t"core_path":' \"DETECT\", >> "$_LPL_PATH"
  echo '\t\t\t"core_name":' \"DETECT\", >> "$_LPL_PATH"
  echo '\t\t\t"crc32":' \"00000000\|crc\", >> "$_LPL_PATH"
  _name=$(basename "$_LPL_PATH")
  echo '\t\t\t"db_name":' \""$_name"\" >> "$_LPL_PATH"
  echo '\t\t}' >> "$_LPL_PATH"

  # next
  (( _count+=1 ))
  #if [ $_count -eq 3 ]; then
  #  break
  #fi
done < "./tmp.txt"

# close json
echo '\t]' >> "$_LPL_PATH"
echo '}' >> "$_LPL_PATH"
rm ./tmp.txt
echo '[.] done!'
