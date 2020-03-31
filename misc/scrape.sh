#!/usr/bin/env sh
if [ "$1" == "" ]; then
	echo 'scrape on rpi/retropie using Skyscraper with screenscraper.fr'
	echo '\tnote1: this is meant to be executed from the roms folder to be scraped, i.e. /some/path/roms/atarijaguar, gamelist.txt and media will be generated there.'
	echo '\tnote2: replace -u in the commandline with your username and password!\n'
	echo 'usage' $0 '<platform> [--cache refresh to refresh cache for the specified platform]'
	exit 1
fi

/opt/retropie/supplementary/skyscraper/Skyscraper --verbosity 3 -s screenscraper -u username:password -t 6 -p "$1" -g . -o ./media "$2" "$3"
