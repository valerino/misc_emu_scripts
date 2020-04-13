# purge_tosec

a tool to ease your emulation collections mantainment!

Using this tool, you can easily cleanup your [TOSEC](https://www.tosecdev.org/) folders from many duplicates like _[a],[b],[o],[h]_ and such (look at the [TOSEC naming convention](https://www.tosecdev.org/tosec-naming-convention)).

usage:

~~~bash
➜  tosec_cleaner (master) ✗ ./purge_tosec.sh
TOSEC Cleaner - purges the given TOSEC set from a,b,o,v,u,m,h dumps.

usage: /Users/valerino/bin/purge_tosec.sh -p <path/to/folder [-t to test run, no deletion] [-h to keep hacks]
        [-a to keep alternates] [-b to force delete [b] anyway]

NOTE:

Before deleting, the script makes sure to delete a file ONLY if at least a "good" copy is kept, either it will keep the "bad".
The only exception is for [b] dumps with the -b option specified (thus, force deletes the only copy which is "bad").
~~~

example:
~~~bash
➜  tosec_cleaner (master) ✗ purge_tosec.sh -t -p ~/Downloads/Commodore\ -\ 128\ \(d64\) -b
[w] forcing deletion of [b]
[w] TEST RUN (no deletion will happen)
[.] using regex: \[(b|o|v|u|m|a|h)(\d*)(\s.+){0,1}]
[.] processing /Users/valerino/Downloads/Commodore - 128 (d64)
[w] SINGLE COPY: /Users/valerino/Downloads/Commodore - 128 (d64)/Empire 128 - Enhanced (1987-10)(Blakemore, Cleve)[h Binary Legens][80column].zip
[w] SINGLE COPY: /Users/valerino/Downloads/Commodore - 128 (d64)/Kiss 128 (19xx)(-)[b].zip
[w] SINGLE COPY, FORCE DELETE /Users/valerino/Downloads/Commodore - 128 (d64)/Kiss 128 (19xx)(-)[b].zip
[.] deleting /Users/valerino/Downloads/Commodore - 128 (d64)/Kiss 128 (19xx)(-)[b].zip
[.] done!
~~~
