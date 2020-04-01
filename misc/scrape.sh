#!zsh
# doesn't work with the default rpi shell, install zsh!
function usage {
	echo 'scrape on rpi/retropie using Skyscraper with screenscraper.fr\n'
	echo 'usage' $0 '<-s to scrape|-g to generate gamelist after -s] <-p platform>'
	echo '\t[-u screenscraper.fr username:password] [-c to refresh cache, only valid with -s]\n'
	echo 'note: gamelist.xml and media will be created in the platorm folder, gamelist.xml will have relative paths both for roms and media.'
}

_DO_GAMELIST=0
_DO_SCRAPE=0
_REFRESH_CACHE=0
while getopts "gscu:p:" arg; do
    case $arg in
        p)
          _PLATFORM="${OPTARG}"
          ;;
        u)
          _USER="${OPTARG}"
          ;;
        c)
          _REFRESH_CACHE=1
          ;;
        g)
          _DO_GAMELIST=1
          ;;
        s)
          _DO_SCRAPE=1
          ;;
        *)
          usage
          exit 1
          ;;
    esac
done

if [ -z "$_PLATFORM" ]; then
	usage
	exit 1
fi

if [ $_DO_GAMELIST -eq 0 ] && [ $_DO_SCRAPE -eq 0 ]; then
	# at least one of -s or -g must be specified
	usage
	exit 1
fi

if [ $_DO_GAMELIST -eq 1 ] && [ $_DO_SCRAPE -eq 1 ]; then
	# only one of -s or -g must be specified
	usage
	exit 1
fi

_SCRAPER='screenscraper'
_SKYSCRAPER='/opt/retropie/supplementary/skyscraper/SkyScraper'
_CMDLINE='--verbosity 3 -p '"$_PLATFORM"
if [ $_DO_SCRAPE -eq 1 ]; then
	# scrape
	_CMDLINE="$_CMDLINE"' -s '"$_SCRAPER"
	if [ ! -z "$_USER" ]; then
		_CMDLINE="$_CMDLINE"' -u '"$_USER"
	fi
	if [ $_REFRESH_CACHE -eq 1 ]; then
		_CMDLINE="$_CMDLINE"' --cache refresh'
	fi
else
	# generate gamelist
	_CMDLINE="$_CMDLINE"' --relative'
fi

# run!
_cmd="$_SKYSCRAPER"' '"$_CMDLINE"
echo '. using commandline:' "$_cmd"
"$_cmd"