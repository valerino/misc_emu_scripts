# mkm3u

useful to create .m3u with uncompressed disks, for retroarch emulators using multi-disk (i.e. lr-vice, lr-puae, ...) given the fact the current implementation do not support mounting compressed disks from Disk Control.

usage:

~~~bash
➜  mkm3u (master) ✗ ./mkm3u.sh                                            
extract all files matching substring and create .m3u with them

usage: ./mkm3u.sh -f <path/to/substring> -d </path/to/destination> [-n m3u name] [-x delete destination first] [-s to skip extract for already unzipped discs]
        if -n is not provided, the provided substring is the name of the generated .m3u
~~~

examples:

~~~bash
➜  mkm3u (master) ✗ ls -l ~/Downloads/test                                                                                     
total 1120
-rwxrwxrwx  1 valerino  staff   66032 24 Dec  1996 1.000 Miglia (1992)(Simulmondo)(Side A)[cr F4CG].zip
-rwxrwxrwx  1 valerino  staff   63034 24 Dec  1996 1.000 Miglia (1992)(Simulmondo)(Side A)[cr ICS].zip
-rwxrwxrwx  1 valerino  staff  161857 24 Dec  1996 1.000 Miglia (1992)(Simulmondo)(Side A)[cr NEI - ICS].zip
-rwxrwxrwx  1 valerino  staff   56362 24 Dec  1996 1.000 Miglia (1992)(Simulmondo)(Side B)[cr F4CG].zip
-rwxrwxrwx  1 valerino  staff   74817 24 Dec  1996 1.000 Miglia (1992)(Simulmondo)(Side B)[cr ICS].zip
-rwxrwxrwx  1 valerino  staff   56384 24 Dec  1996 1.000 Miglia (1992)(Simulmondo)(Side B)[cr NEI - ICS].zip
-rw-------  1 valerino  staff   56231 17 Mar 15:43 Seven Cities of Gold (1984)(Electronic Arts)(Side A).d64.zip
-rw-------  1 valerino  staff   21043 17 Mar 15:43 Seven Cities of Gold (1984)(Electronic Arts)(Side B).d64.zip

# extracting zips
➜  mkm3u (master) ✗ ./mkm3u.sh -f ~/Downloads/test/Seven\ Cities\ of\ Gold\ \(1984\)\(Electronic\ Arts\) -d ~/Downloads/game -x   
[.] extracting all files matching /Users/valerino/Downloads/test/Seven Cities of Gold (1984)(Electronic Arts) to /Users/valerino/Downloads/game
[.] generating m3u: /Users/valerino/Downloads/game/Seven Cities of Gold (1984)(Electronic Arts).m3u
[.] done!
➜  mkm3u (master) ✗ cat /Users/valerino/Downloads/game/Seven\ Cities\ of\ Gold\ \(1984\)\(Electronic\ Arts\).m3u               
/Users/valerino/Downloads/game/Seven Cities of Gold (1984)(Electronic Arts)(Side A).d64
/Users/valerino/Downloads/game/Seven Cities of Gold (1984)(Electronic Arts)(Side B).d64

# do not extract, use sources directly
➜  mkm3u (master) ✗ ./mkm3u.sh -f ~/Downloads/test/Seven\ Cities\ of\ Gold\ \(1984\)\(Electronic\ Arts\) -d ~/Downloads/game -x -s
[.] generating m3u: /Users/valerino/Downloads/game/Seven Cities of Gold (1984)(Electronic Arts).m3u
[.] done!
➜  mkm3u (master) ✗ cat /Users/valerino/Downloads/game/Seven\ Cities\ of\ Gold\ \(1984\)\(Electronic\ Arts\).m3u                  
/Users/valerino/Downloads/test/Seven Cities of Gold (1984)(Electronic Arts)(Side B).d64.zip
/Users/valerino/Downloads/test/Seven Cities of Gold (1984)(Electronic Arts)(Side A).d64.zip
~~~

## special note for Android
. needs rooted device and a terminal emulator (of course!)
. copy the script to /data/local/tmp and use from there.
. /data/local/tmp must be writable: __su -c chmod 777 /data/local/tmp__

__no checks are made regarding the .zips content, make sure to use zips containing each exactly ONE disk image (TOSEC collections are one zip/one disc already).__