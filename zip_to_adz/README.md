# zip-2-adz

useful for Amiga TOSEC collections, turn _zipped .ADF_ to compressed _.ADZ_ to be used with lr-puae Amiga emulator.

__using .ADZ for compression makes lr-puae disk-control mounter working for multi-disks !__

usage:

~~~bash
➜ zip_to_adz ./zip_to_adz.sh             
turn all zipped .ADF in the given folder to .ADZ

usage: ./zip_to_adz.sh -p <path/to/folder> [-b to break on error] [-z use 7z instead of unzip] [-t to test run, no deletion of source .ZIPs]
~~~

__beware to use zips containing each exactly ONE .adf, no checks are made (TOSEC collections are one zip/one adf already).__