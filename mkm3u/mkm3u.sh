#!/usr/bin/env sh
function usage {
    echo 'extract all files matching substring and create .m3u\n'
    echo 'usage:' "$0" '-f <path/to/substring> -d </path/to/destination> [-n m3u name] [-x delete destination first] [-s to skip extract for already unzipped discs]'
    echo '\t[-l limit to n entries, i.e. 10]\n'
    echo 'if -n is not provided, the provided substring is the name of the generated .m3u'
}
_DELETE_DEST=0
_SKIP_EXTRACT=0
_LIMIT=0
while getopts "xsf:d:n:l:" arg; do
    case $arg in
        l)
          _LIMIT="${OPTARG}"
          ;;
        f)
          _PATH="${OPTARG}"
          ;;
        d)
          _DEST="${OPTARG}"
          ;;
        n)
          _M3UNAME="${OPTARG}"
          ;;
        x)
          _DELETE_DEST=1
          ;;
        s)
          _SKIP_EXTRACT=1
          ;;
        *)
          usage
          exit 1
          ;;
    esac
done

if [ "$_PATH" == "" ] || [ "$_DEST" == "" ]; then
  usage
  exit 1
fi

# remove destination first if asked to
if [ $_DELETE_DEST -eq 1 ]; then
  rm -rf "$_DEST"
fi
mkdir -p "$_DEST"

# generate m3u path
_parent=$(dirname "$_PATH")
_tofind=$(basename "$_PATH")
if [ "$_M3UNAME" == "" ]; then
  _M3UPATH="$_DEST"/"$_tofind".m3u
else
  _M3UPATH="$_DEST"/"$_M3UNAME"
fi

if [ $_SKIP_EXTRACT -eq 0 ]; then
  # extract first
  echo '[.] extracting all files matching' "$_PATH" 'to' "$_DEST"
  find "$_parent" | grep "$_tofind" > ./tmp.txt
  if [ $? -ne 0 ]; then
    echo '[x] wrong input, or no matches found!'
    rm ./tmp.txt
    exit 1
  fi
  _n=0
  while IFS= read -r line
  do
    unzip "$line" -d "$_DEST"
    if [ $? -ne 0 ]; then
      # error extraction
      exit 1
    fi
    _n+=1
    if [ $_LIMIT -ne 0 ]; then
      if [ $_n -eq $_LIMIT ]; then
        break
      fi
    fi
  done < "./tmp.txt"
  rm ./tmp.txt
fi

# now read all files in the dir and create the m3u
echo '[.] generating m3u:' "$_M3UPATH"

if [ $_SKIP_EXTRACT -eq 0 ]; then
  # default, find in the extracted folder
  find "$_DEST"/* > ./tmp.txt
else
  # use the source folder directly 
  find "$_parent" | grep "$_tofind" > ./tmp.txt
fi

while IFS= read -r line
do
  echo "$line" >> "$_M3UPATH"
done < "./tmp.txt"
rm ./tmp.txt

echo '[.] done!'
