# rezip

rezip files in a folder (unzip + rezip making a big zip of everything), discarding subdirectories.

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
rezip files in the given zip to a single zipfile.
usage: ./rezip.sh -p <path/to/src_zip> [-o destination zip|destination dir (source path basename will be used), default is to overwrite source zip]
  [-z to use 7z] [-c to unzip EVERY ZIP FILE contained into the source file as well, and delete such zip then] [-i to ignore unzip errors]

# example 
➜ ~/repos/misc_emu_scripts (master) ✗ ~/repos/misc_emu_scripts/rezip/rezip.sh -p /media/valerino/Elements/Apple/Macintosh/Apple\ Macintosh\ -\ Applications\ -\ \[IMG\]\ \(TOSEC-v2019-09-01\).zip -o ~/Downloads -i
[.] unzipping /media/valerino/Elements/Apple/Macintosh/Apple Macintosh - Applications - [IMG] (TOSEC-v2019-09-01).zip
[.] rezipping /media/valerino/Elements/Apple/Macintosh/Apple Macintosh - Applications - [IMG] (TOSEC-v2019-09-01).zip to /home/valerino/Downloads/Apple Macintosh - Applications - [IMG] (TOSEC-v2019-09-01).zip
  adding: KaleidaGraph (1994)(Abelbeck Software)(Disk 1 of 2)[sn 146745].img (deflated 25%)
  adding: Adobe Photoshop Limited Edition v2.5 (1994)(Adobe)(Disk 1 of 3).img (deflated 45%)
  adding: Adobe Photoshop Limited Edition v2.5 (1994)(Adobe)(Disk 3 of 3).img (deflated 3%)
  adding: microPrint Manager v1.0 (1994)(Sonic Systems).img (deflated 98%)
  adding: LabVIEW for Power Macintosh - v3.1 to v3.1.1 Updater (1995)(National Instruments)(Disk 2 of 2)[pn 500079A-02].img (deflated 7%)
  adding: MacBTX 1&1 (1994)(1&1 Telekommunikation)(DE).img (deflated 39%)
  adding: KaleidaGraph (1994)(Abelbeck Software)(Disk 2 of 2)[sn 146745].img (deflated 36%)
  adding: LabVIEW for Power Macintosh - v3.1 to v3.1.1 Updater (1995)(National Instruments)(Disk 1 of 2)[pn 500079A-01].img (deflated 10%)
  adding: Adobe Photoshop Limited Edition v2.5 (1994)(Adobe)(Disk 2 of 3).img (deflated 3%)
  adding: MacDraw vD2-1.9.5 (1986)(Apple)(DE).img (deflated 64%)
  adding: America Online for Macintosh v2.7 (1996)(America Online).img (deflated 6%)
  adding: LabVIEW for 68K Macintosh - v3.1 to v3.1.1 Updater (1995)(National Instruments)[pn 500084A-01].img (deflated 7%)
[.] done, created /home/valerino/Downloads/Apple Macintosh - Applications - [IMG] (TOSEC-v2019-09-01).zip !
~~~

> using the -c flag assumes the source zip also contain zip files, which are undividually unzipped in the process (and their corresponding zip deleted).
