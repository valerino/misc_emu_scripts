# scrape

basically a wrapper for [Skyscraper](https://github.com/muldjord/skyscraper) specifically tailored to scrape using [screenscraper](https://www.screenscraper.fr).

usage:

~~~bash
# to use on rpi directly, use bash /path/to/scrape.sh
➜  misc_emu_scripts (master) ✗ ./scrape/scrape.sh                               
scrape on rpi/retropie using Skyscraper with screenscraper.fr

usage ./scrape/scrape.sh <-s to scrape|-g to generate gamelist after -s] <-p platform> [-d do not descend in subdirs]
        [-u screenscraper.fr username:password, expects -s] [-f /path/to/file to scrape single file, expects -s] [-c to refresh cache, expects -s]
        [-a add extensions space separated i.e. "*.chd *.m3u"] [-x exclude wildcards comma-separated i.e. "*.adz,*.zip"] [-i include wildcards comma-separated i.e. "*.adz,*.zip"]
        [-n for interactive]

note: gamelist.xml and media will be created in the platorm folder, gamelist.xml will have relative paths both for roms and media.
~~~

