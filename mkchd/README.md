# mkchd

creates .CHD cd-rom images for mame and other emulators from .cue/.bin images.

* includes [precompiled binary of chdman for macos](./chdman_macos), must be put somewhere in path as _chman_
  ~~~bash
  ➜  mkchd (master) ✗ ln -s ~/repos/misc_emu_scripts/build_chd/chdman_macos ~/bin/chdman
  ~~~

usage:

~~~bash
➜  mkchd (master) ✗ ./build_cdh.sh
converts .cue/.bin cd to .chd format
usage: ./mkchd.sh <path/to/cue> <path/to/destination_chd>
~~~

sample usage:

~~~bash
./mkchd.sh ~/Downloads/R-Type\ Complete\ CD\ \(Japan\)/R-Type\ Complete\ CD\ \(Japan\).cue ~/Downloads/R-Type\ Complete\ CD\ \(Japan\).chd
~~~
