# batch_zip

zip all files in the given directory.

usage:

~~~bash
➜  batch_zip (master) ✗ ./batch_zip.sh
zip all (non compressed) files in the given folder

usage: ./batch_zip.sh -p <path/to/folder> [-b to break on error] [-z use 7z instead of zip] [-d to delete source files] [-m to move compressed files one folder up once generated] [-s to delete the containing folder after moving, to be used with -m] [-t to test run] [-i <default|csv> ignore common companion files or ignore a custom csv list of extensions] [-a <csv> add only the specified extensions (case-insensitive csv list like .txt,.md,.png,...)]
~~~
