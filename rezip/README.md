# rezip

rezip files in a folder, discarding subdirectories.

1. unzip source zip.
2. assuming the following structure:

~~~bash
--> source_zip_folder
    ---> dir 1
        ---> file1
        ---> file2
        ---> ...
    ---> dir 2
        ---> file3
        ---> file4
        ---> ...
    ---> ...
~~~

3. destination zip is created as:

~~~bash 
--> dest zip
    ---> file1
    ---> file2
    ---> file3
    ---> file4
    ---> ...
~~~

~~~bash
➜  rezip (master) ✗ ./rezip.sh
rezip files in the given zip.

usage: ./rezip/rezip.sh -p <path/to/src_zip> [-o destination zip, default is to overwrite source] [-z to unzip individual files and delete the zips] [-i to ignore unzip errors]
~~~

> using the -z flag assumes the source zip also contain zip files, which are undividually unzipped in the process (and their corresponding zip deleted).