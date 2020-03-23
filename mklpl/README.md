# mklpl

creates Retroarch playlist (JSON format, Retoarch > 1.7.6 only) from the given folder, very fast because it doesn't scan the file.

usage:

~~~bash
➜  mklpl (master) ✗ ./mklpl.sh
generates retroarch (> 1.7.6, json) .LPL playlist

usage: ./mklpl.sh -p <path/to/folder_to_scan> <-s path/to/parent/folder_on_destination_machine> -d </path/to/playlist>
        <-c /path/to/core_on_destination_machine> <-n core_name>
        [-l label_display_mode, default 0] [-r right_thumbnail_mode, default 0] [-t left_thumbnail_mode, default 0]
        [-x /path/to/merge file to use in another invocation] [-y input merge file previously generated with -x]

path specified with -s must be the parent path on the destination machine where folder_to_scan is.

if -x is specified, merge_file is generated and can be specified with -y to generate another merged playlist.
NOTE: to be sorted correctly, both the paths in merge_file generated with -x and the -p path in the new invocation must have the same depth!

when -x is specified, every other parameters are ignoted except -p and -y.
if both -x and -y are specified, merge_file is read in input, merged with the content of the path at -p and rewritten.
~~~

examples

~~~bash
# generate playlist using local folder "/Users/valerino/Downloads/Commodore - 64 (crt)",
# pointing to remote folder "/storage/roms/ext-roms/Commodore - 64 (crt)"
./mklpl.sh -p "/Users/valerino/Downloads/Commodore - 64 (crt)" -d "./Commodore - 64 (crt).lpl" -c "/tmp/cores/vice_x64_libretro.so" -n "Commodore - 64" -s "/storage/roms/ext-roms"
~~~

~~~bash
# generate merge file from "/Users/valerino/Downloads/Commodore - 64 (crt)"
./mklpl.sh -p "/Users/valerino/Downloads/Commodore - 64 (crt)" -x ./crt.txt
~~~

~~~bash
# generate merge file from "/Users/valerino/Downloads/Commodore - 64 (tap)" and merge with the previous
./mklpl.sh -p "/Users/valerino/Downloads/Commodore - 64 (crt)" -y ./crt.txt -x ./merge.txt
~~~

~~~bash
# generate playlist using local folder "/Users/valerino/Downloads/Commodore - 64 (dsk)",
# pointing to remote folder "/storage/roms/ext-roms/Commodore - 64 (dsk)" and merging with the above merge file
./mklpl.sh -p "/Users/valerino/Downloads/Commodore - 64 (crt)" -d "./Commodore - 64 (crt).lpl" -c "/tmp/cores/vice_x64_libretro.so" -n "Commodore - 64" -s "/storage/roms/ext-roms" -y ./merge.txt
~~~