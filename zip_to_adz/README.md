# zip-2-adz

useful for Amiga TOSEC collections, turn _.zips_ to compressed _.adzs_.

__using .ADZ for compression makes Retroarch disk-control mounter working for multi-disks !__

usage:

~~~bash
➜  zip_to_adz ./zip_to_adz.sh             
turn all .ZIP in the given folder to .ADZ

usage: ./zip_to_adz.sh -p <path/to/folder> [-b to break on error] [-t to test run, no deletion of source .ZIPs]
~~~

__beware to use zips containing each exactly ONE .adf, no checks are made (TOSEC collections are one zip/one adf already).__