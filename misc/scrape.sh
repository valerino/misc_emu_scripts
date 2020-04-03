#!zsh
# doesn't work with the default rpi shell, install zsh!
function usage {
	echo 'scrape on rpi/retropie using Skyscraper with screenscraper.fr\n'
	echo 'usage' $0 '<-s to scrape|-g to generate gamelist after -s] <-p platform>'
	echo '\t[-u screenscraper.fr username:password, expects -s] [-f /path/to/file to scrape single file, expects -s] [-c to refresh cache, expects -s]\n'
	echo 'note: gamelist.xml and media will be created in the platorm folder, gamelist.xml will have relative paths both for roms and media.'
}

_DO_GAMELIST=0
_DO_SCRAPE=0
_REFRESH_CACHE=0
while getopts "gscu:p:f:" arg; do
    case $arg in
        p)
          _PLATFORM="${OPTARG}"
          ;;
        f)
          _FILEPATH="${OPTARG}"
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

_SCRAPER="screenscraper"
_SKYSCRAPER="/opt/retropie/supplementary/skyscraper/Skyscraper"
set -- "$_SKYSCRAPER"
set -- "$@" --verbosity 3 --addext "*.chd" -p "$_PLATFORM"
if [ $_DO_SCRAPE -eq 1 ]; then
	# scrape
	set -- "$@" -s "$_SCRAPER"
	if [ ! -z "$_USER" ]; then
		set -- "$@" -u "$_USER"
	fi
	if [ ! -z "$_FILEPATH" ]; then
		set -- "$@" -f "$_FILEPATH"
	fi
	if [ $_REFRESH_CACHE -eq 1 ]; then
		set -- "$@" --cache refresh
	fi
else
	set -- "$@" --relative
fi

# run!
echo '. using commandline:' "$@"
"$@"