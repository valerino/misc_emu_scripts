# batch_archive

Recursively extract ZIP, 7z, and LHA files, including nested archives, then create
one ZIP or 7z archive containing the extracted files rather than the source
archives. Extracted archives are not included in the output archive, only their
contents. The default output is a sibling of the input directory, so it cannot
be added to or deleted from its own archive.

Requires Python 3 plus `unzip`, `zip`, `7z` on `PATH`. On Arch Linux:

```bash
sudo pacman -S unzip zip 7z1
```

## Examples

Example keep.txt

```gitignore
*.chd
*.iso
```

Create `202608.zip` beside `202608/` as `202608.zip`, leaving `202608/neogeocd` which contains `.chd` files, delete everything else:

```bash
# only 202608/neogeocd/game.chd remains (and is not included in 202608.zip)
./batch_archive.py ./202608 --no-touch ./keep.txt --delete

# leaves input untouched 
./batch_archive.py ./202608 --no-touch ./keep.txt

```

Preview all extraction, archiving, and deletion commands without changing
files:

```bash
./batch_archive.py roms --test
```

Without `--delete`, protected paths are never extracted, deleted, or included
in the output archive; they remain in place. Extracted archives are excluded
from the output and the extracted contents are deleted after archiving.
Patterns are
gitignore-like: blank lines and `#` comments
are ignored; `!` re-includes an earlier match; patterns containing `/` are
relative to the input directory; and a trailing `/` applies recursively. When
`--no-touch` is omitted, `./notouch.txt` is used if it exists in the current
directory.

With `--delete`, everything in the input directory except files matched by
`--no-touch` is deleted after successful archive creation; the input directory
itself is removed once it becomes empty. Add `--backup` to first copy the
untouched input directory to a sibling directory named
`INPUT_DIRECTORY.backup/`; it will not overwrite an existing backup.

Run `./batch_archive.py --help` for every option. The small regression check
can be run with `python3 test_batch_archive.py`.

Large directories are passed to the archiver in bounded argument batches, so
they do not hit the operating system command-line limit. ZIP preserves unusual
filenames; 7z rejects filenames containing a newline because 7z rewrites them.
