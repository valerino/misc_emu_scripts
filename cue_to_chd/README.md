# cue2chd

turns .cue/.bin images to chd, processing the whole input directory/directories (also unzip if files are zipped)

> needs chdman

usage:

~~~bash
./cue2chd.sh
convert .CUE/BIN images to CHD.\n
usage: ./cue2chd.sh -p <path/to/sourcedir> -o </path/to/destination> [-z sourcedir have zips] [-d delete zips/dirs] [-i ignore errors] [-t to testrun]
~~~

example:

~~~bash
# input files are in separated directories with .cue/.bin
./cue2chd.sh -p /Users/valerino/Desktop/cd32 -o ~/Desktop/out -d

# input files are zipped (will be unzipped first)
./cue2chd.sh -p /Users/valerino/Desktop/cd32 -o ~/Desktop/out -d -z

~~~
