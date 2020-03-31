#!/usr/bin/env sh
if [ $# -lt 1 ]; then
	echo 'scrape on rpi/retropie using Skyscraper with screenscraper.fr'
	echo '\tnote1: gamelist.xml and media will be created in the platorm folder, gamelist.xml will have relative paths both for roms and media.'
	echo '\tnote2: replace -u in the commandline with your username and password!\n'
	echo 'usage' $0 '<platform> [--cache refresh to refresh cache for the specified platform]'
	exit 1
fi

/opt/retropie/supplementary/skyscraper/Skyscraper --verbosity 3 -s screenscraper -u username:password -t 6 -p "$1" --relative "$2" "$3"
