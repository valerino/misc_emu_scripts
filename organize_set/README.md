# organize_set

better version of purge_tosec.sh :)

supports unarchiving + moving files to alphabetic folders with up to 255 files each (to support i.e. c64mini/maxi).

usage:

~~~bash
➜  organize_set (master) ✗ ./organize_set.py --help
usage: organize_set.py [-h] --src SRC --dst DST --flags FLAGS

organize romsets.

optional arguments:
  -h, --help     show this help message and exit
  --src SRC      folder to operate on
  --dst DST      destination folder, same as --src if not specified.
  --flags FLAGS  unarchive,delarchives,movealpha,moveunalpha,skipbad,skipalt,delskipped,test).
  
# unarchive and alphadir files to ~/Downloads/test, skipping bad ([b...]) and alts ([a...]). no source files are touched.
# results in dirs list ~/Downloads/test/A1,A2,A3,B1,B2,....
./organize_set.py --dst ~/Downloads/test --flags unarchive,delarchives,skipbad,skipalt,movealpha --src ~/Downloads/Commodore\ C64\ -\ Games\ -\ \[D64\]
~~~
