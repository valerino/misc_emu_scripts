#!/usr/bin/env bash
# doesn't work with the default rpi shell, install zsh!
function usage {
	echo 'scrape on rpi/retropie using Skyscraper with screenscraper.fr\n'
	echo 'usage' $1 '<-s to scrape|-g to generate gamelist after -s] <-p platform> [-d do not descend in subdirs]'
	echo '\t[-u screenscraper.fr username:password, expects -s] [-f /path/to/file to scrape single file, expects -s] [-c to refresh cache, expects -s]'
	echo '\t[-a add extensions space separated i.e. "*.chd *.m3u"] [-x exclude wildcards comma-separated i.e. "*.adz,*.zip"] [-i include wildcards comma-separated i.e. "*.adz,*.zip"]'
  echo '\t[-t sets roms path, if different than platform] [-n for interactive] [-l relaunch with -g after scraping with -s to generate gamelist.xml in one shot\n'
  echo '\t[-k to include skipped games anyway] [-j to force using filenames for gamelist, instead of the scraped name]\n'
	echo 'note: gamelist.xml and media will be created in the platorm folder, gamelist.xml will have relative paths both for roms and media.'
}

_DO_GAMELIST=0
_DO_SCRAPE=0
_REFRESH_CACHE=0
_NOSUBDIRS=0
_INTERACTIVE=0
_INCLUDE_SKIPPED=0
_USE_FILENAME=0
_RELAUNCH=0
while getopts "gnsjklcu:t:p:f:x:i:a:d" arg; do
    case $arg in
        d)
          _NOSUBDIRS=1
          ;;
        k)
          _INCLUDE_SKIPPED=1
          ;;
        j)
          _USE_FILENAME=1
          ;;
        t)
          _INPUT_PATH="${OPTARG}"
          ;;
        l)
          _RELAUNCH=1
          ;;
        n)
          _INTERACTIVE=1
          ;;
        p)
          _PLATFORM="${OPTARG}"
          ;;
        i)
          _INCLUDE="${OPTARG}"
          ;;
        x)
          _EXCLUDE="${OPTARG}"
          ;;
        a)
          _ADDEXT="${OPTARG}"
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
          usage "$0"
          exit 1
          ;;
    esac
done

if [ -z "$_PLATFORM" ]; then
	usage "$0"
	exit 1
fi

if [ $_DO_GAMELIST -eq 0 ] && [ $_DO_SCRAPE -eq 0 ]; then
	# at least one of -s or -g must be specified
	usage "$0"
	exit 1
fi

if [ $_DO_GAMELIST -eq 1 ] && [ $_DO_SCRAPE -eq 1 ]; then
	# only one of -s or -g must be specified
	usage "$0"
	exit 1
fi

_SCRAPER="screenscraper"
_SKYSCRAPER="/opt/retropie/supplementary/skyscraper/Skyscraper"
set -- "$_SKYSCRAPER"
set -- "$@" --verbosity 3 -p "$_PLATFORM"

if [ ! -z "$_ADDEXT" ]; then
	set -- "$@" --addext "$_ADDEXT"
fi
if [ ! -z "$_EXCLUDE" ]; then
	set -- "$@" --excludefiles "$_EXCLUDE"
fi
if [ ! -z "$_INCLUDE" ]; then
	set -- "$@" --includefiles "$_INCLUDE"
fi
if [ ! -z "$_INPUT_PATH" ]; then
	set -- "$@" -i "$_INPUT_PATH"
fi
if [ "$_INCLUDE_SKIPPED" -eq 1 ]; then
  set -- "$@" --skipped
fi
if [ "$_USE_FILENAME" -eq 1 ]; then
  set -- "$@" --forcefilename
fi
if [ "$_NOSUBDIRS" -eq 1 ]; then
	set -- "$@" --nosubdirs
fi

if [ $_DO_SCRAPE -eq 1 ]; then
	# scrape
	set -- "$@" -s "$_SCRAPER"
	if [ ! -z "$_USER" ]; then
		set -- "$@" -u "$_USER"
	fi
	if [ $_REFRESH_CACHE -eq 1 ]; then
		set -- "$@" --cache refresh
	fi
	if [ $_INTERACTIVE -eq 1 ]; then
		set -- "$@" --interactive
	fi  
  # add single rom in the end if any
  if [ ! -z "$_FILEPATH" ]; then
		set -- "$@" "$_FILEPATH"
	fi

else
	set -- "$@" --relative
fi

# run!
echo '. using commandline:' "$@"
"$@"
if [ "$?" -ne 0 ]; then
  exit 1
fi

if [ "$_RELAUNCH" -eq 1 ]; then
  set -- "$_SKYSCRAPER"
  set -- "$@" --verbosity 3 --relative -p "$_PLATFORM"

  if [ ! -z "$_ADDEXT" ]; then
	  set -- "$@" --addext "$_ADDEXT"
  fi
  if [ "$_INCLUDE_SKIPPED" -eq 1 ]; then
    set -- "$@" --skipped
  fi
  if [ "$_USE_FILENAME" -eq 1 ]; then
    set -- "$@" --forcefilename
  fi
  if [ ! -z "$_INPUT_PATH" ]; then
	  set -- "$@" -i "$_INPUT_PATH"
  fi

  # run!
  echo '. relaunching:' "$@"
  "$@"
fi
