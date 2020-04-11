# fix_gamelist


fixes gamelist.xml removing :

* non-existent entries (missing file)
* entries without image / description

usage:

~~~bash
➜  fix_gamelist (master) ✗ ./fix_gamelist.py --help
usage: fix_gamelist.py [-h] --xml XML [--out OUT] [--interactive]
                       [--check_path] [--check_image] [--check_cover]
                       [--check_desc] [--alt] [--alt2] [--delete_files]

cleanup gamelist.xml of missing entries, for EmulationStation et al.

    by specifying --check_path, --check_image, --check_cover it will check entry path/image/cover tags and their associated filepath.
    by specifying --check_desc, it will check also for missing game description.
    if any of these check is specified and fails, the entry is flagged to be removed.
    
    all the check_flags are ignored if one of the --alt or --alt2 flags is specified:

    by specifying --alt, an entry is kept only if path and the associated file exists AND at least one image/cover exists.
    by specifying --alt2, an entry is kept only if path and the associated file exists AND at least one image/cover/desc exists.
    

optional arguments:
  -h, --help      show this help message and exit
  --xml XML       source gamelist.xml
  --out OUT       destination gamelist.xml (default overwrites)
  --interactive   ask confirmation before removing an entry
  --check_path    remove entries with missing "path" tag or file
  --check_image   remove entries with missing "image" tag or file
  --check_cover   remove entries with missing "cover" tag or file
  --check_desc    remove entries with missing "desc" tag or content
  --alt           all check_* flags are ignored, an entry is kept only if path exist AND at least one image/cover exists
  --alt2          all check_* flags are ignored, an entry is kept only if path exist AND at least one image/cover/desc exists
  --delete_files  remove also files associated with path/image/cover when removing the entry
~~~

sample usage:

~~~bash
~/RetroPie/roms/atari5200 » ~/fix_gamelist.py --xml ./gamelist.xml --check_image --check_path
[.] processing IN=./gamelist.xml, OUT=./gamelist.xml, check_path=True, check_image=True, check_cover=False, check_desc=False, interactive=False, delete_files=False)
[.] DELETED entry=5200 Menu (USA)(Proto) (has_path=True, has_image=False, has_cover=False, has_desc=False)
[.] DELETED entry=Atari PAM - Pete's Test (USA) (has_path=True, has_image=False, has_cover=False, has_desc=False)
[.] DELETED entry=Atari PAM Diagnostics (USA)(v2.0) (has_path=True, has_image=False, has_cover=False, has_desc=False)
[.] DELETED entry=Atari PAM Diagnostics (USA)(v2.3) (has_path=True, has_image=False, has_cover=False, has_desc=False)
[.] DELETED entry=Atari PAM System Test (USA)(v1.02) (has_path=True, has_image=False, has_cover=False, has_desc=False)
[.] DELETED entry=Boogie (USA)(Demo) (has_path=True, has_image=False, has_cover=False, has_desc=False)
[.] DELETED entry=RealSports Baseball (USA) (has_path=True, has_image=False, has_cover=False, has_desc=True)
[.] DELETED entry=Yellow Submarine (USA)(Demo) (has_path=True, has_image=False, has_cover=False, has_desc=False)
[.] Done!
~~~

or using interactive mode:

~~~bash
~/RetroPie/roms/atari2600 » ~/fix_gamelist.py --xml ./gamelist.xml --check_image --check_desc --check_path --interactive --out ./gamelist-clean.xml
[.] processing IN=./gamelist.xml, OUT=./gamelist-clean.xml, check_path=True, check_image=True, check_cover=False, check_desc=True, interactive=True, delete_files=False)
[?] OK TO DELETE entry=Bouncin' Baby Bunnies (USA)(Proto) (has_path=True, has_image=False, has_cover=False, has_desc=False) ? [Y/n] y
[.] DELETED entry=Bouncin' Baby Bunnies (USA)(Proto) (has_path=True, has_image=False, has_cover=False, has_desc=False)
[?] OK TO DELETE entry=City Defender (USA) (has_path=True, has_image=True, has_cover=False, has_desc=False) ? [Y/n] n
[?] OK TO DELETE entry=Color Bar Generator (USA) (has_path=True, has_image=False, has_cover=False, has_desc=False) ? [Y/n] y
[.] DELETED entry=Color Bar Generator (USA) (has_path=True, has_image=False, has_cover=False, has_desc=False)
[?] OK TO DELETE entry=Crazy Combat (Europe) (has_path=True, has_image=True, has_cover=False, has_desc=False) ? [Y/n] n
[?] OK TO DELETE entry=Frog Demo (Europe) (has_path=True, has_image=False, has_cover=False, has_desc=False) ? [Y/n] y
[.] DELETED entry=Frog Demo (Europe) (has_path=True, has_image=False, has_cover=False, has_desc=False)
[?] OK TO DELETE entry=Going-up?? (USA)(Proto) (has_path=True, has_image=True, has_cover=False, has_desc=False) ? [Y/n] n
[?] OK TO DELETE entry=Good Luck, Charlie Brown (USA)(Proto) (has_path=True, has_image=True, has_cover=False, has_desc=False) ? [Y/n] n
[?] OK TO DELETE entry=Looping (USA)(Proto) (has_path=True, has_image=True, has_cover=False, has_desc=False) ? [Y/n] n
[?] OK TO DELETE entry=MagiCard (USA) (has_path=True, has_image=False, has_cover=False, has_desc=False) ? [Y/n] y
[.] DELETED entry=MagiCard (USA) (has_path=True, has_image=False, has_cover=False, has_desc=False)
[?] OK TO DELETE entry=Morse Code Tutor (USA) (has_path=True, has_image=False, has_cover=False, has_desc=False) ? [Y/n] y
[.] DELETED entry=Morse Code Tutor (USA) (has_path=True, has_image=False, has_cover=False, has_desc=False)
[?] OK TO DELETE entry=Power Lords (USA)(Proto) (has_path=True, has_image=False, has_cover=False, has_desc=False) ? [Y/n] y
[.] DELETED entry=Power Lords (USA)(Proto) (has_path=True, has_image=False, has_cover=False, has_desc=False)
[?] OK TO DELETE entry=Pursuit of the Pink Panther (USA)(Proto) (has_path=True, has_image=False, has_cover=False, has_desc=False) ? [Y/n] y
[.] DELETED entry=Pursuit of the Pink Panther (USA)(Proto) (has_path=True, has_image=False, has_cover=False, has_desc=False)
[?] OK TO DELETE entry=See Saw (Europe) (has_path=True, has_image=True, has_cover=False, has_desc=False) ? [Y/n] n
[?] OK TO DELETE entry=Sky Alien (Europe) (has_path=True, has_image=True, has_cover=False, has_desc=False) ? [Y/n] n
[?] OK TO DELETE entry=Treasure Island (Europe) (has_path=True, has_image=True, has_cover=False, has_desc=False) ? [Y/n] n
[?] OK TO DELETE entry=Turbo (USA)(Proto) (has_path=True, has_image=True, has_cover=False, has_desc=False) ? [Y/n] n
[?] OK TO DELETE entry=Unknown Datatech Game (USA)(Proto) (has_path=True, has_image=True, has_cover=False, has_desc=False) ? [Y/n] n
[?] OK TO DELETE entry=X'mission (USA) (has_path=True, has_image=True, has_cover=False, has_desc=False) ? [Y/n] n
[?] OK TO DELETE entry=Zoo Keeper Sounds (USA)(Proto) (has_path=True, has_image=False, has_cover=False, has_desc=False) ? [Y/n] n
[.] Done!
~~~
