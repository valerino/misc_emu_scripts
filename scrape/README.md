# scrape

basically a wrapper for [Skyscraper](https://github.com/muldjord/skyscraper) specifically tailored to scrape using [screenscraper](https://www.screenscraper.fr).

usage:

~~~bash
# to use on rpi directly, use bash /path/to/scrape.sh
➜  misc_emu_scripts (master) ✗ ./scrape/scrape.sh                               
scrape on rpi/retropie using Skyscraper with screenscraper.fr

usage /home/pi/scripts/scrape/scrape.sh <-s to scrape|-g to generate gamelist after -s] <-p platform> [-d do not descend in subdirs]
        [-u screenscraper.fr username:password, expects -s] [-f /path/to/file to scrape single file, expects -s] [-c to refresh cache, expects -s]
        [-a add extensions space separated i.e. "*.chd *.m3u"] [-x exclude wildcards comma-separated i.e. "*.adz,*.zip"] [-i include wildcards comma-separated i.e. "*.adz,*.zip"]
        [-n for interactive] [-l relaunch with -g after scraping to generate gamelist.xml in one shot

note: gamelist.xml and media will be created in the platorm folder, gamelist.xml will have relative paths both for roms and media.
~~~

sample usage:

~~~bash
# you put a new .m3u in the roms folder and you want to add it to the gamelist, in one shot:

~ » bash ~/scripts/scrape/scrape.sh -u valerino:xoanino -p 3do -a "*.m3u" -l
. using commandline: /opt/retropie/supplementary/skyscraper/Skyscraper --verbosity 3 -p 3do --addext *.m3u --relative

....
~~~