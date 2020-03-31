
#!/usr/bin/env sh
# converts .cue/.bin cd to .chd format (needs chdman somewhere in path)

if [ $# -lt 2 ]; then
	echo 'converts .cue/.bin cd to .chd format'
	echo 'usage:' $0 '<path/to/cue> <path/to/destination_chd>'
	exit 1
fi

chdman createcd -i "$1" -o "$2"


