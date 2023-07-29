# zippedcue2chd

turns zipped .cue/.bin images to chd, processing the whole input directory (unzip, make chd)

> needs chdman

usage:

~~~bash
 ./zipcue2chd.sh
convert zipped .CUE/BIN images to CHD.
usage: ./zipcue2chd.sh -p <path/to/dir_with_zipped_cuebin> -o </path/to/destination> [-d delete zips] [-i ignore errors]
~~~

example:

~~~bash
./zipcue2chd.sh -p /Volumes/Elements/Sega/Dreamcast/redump_dc_revival -o /Volumes/Elements/Sega/Dreamcast/redump_dc_revival -d
~~~
