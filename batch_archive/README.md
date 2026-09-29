# batch_archive

Recursively extract ZIP, 7z, RAR, TAR.GZ and LHA files, including nested archives, then create
one ZIP or 7z archive containing the extracted files rather than the source
archives. Extracted archives are not included in the output archive, only their
contents. The default output is a sibling of the input directory, so it cannot
be added to or deleted from its own archive.

Requires Python 3 plus `unzip`, `zip`, `7z`, and `tar` on `PATH`. On Arch Linux:

```bash
sudo pacman -S unzip zip 7z1 tar
```

`tar` is only invoked for `.tar.gz` archives; `unzip` only for `.zip`; `7z`
only for `.7z`/`.rar`/`.lha` inputs or `--format 7z` output.

## Examples

Example keep.txt

```gitignore
*.chd
*.iso
somedirectory
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
Patterns are gitignore-like, matched with `fnmatch` (so `*`, `?`, `[...]`
work; `*` also crosses `/`): blank lines and `#` comments are ignored; a
leading `/` is stripped; `!` re-includes a path matched by an earlier pattern
(last match wins); patterns containing `/` are matched against the path
relative to the input directory; other patterns match the relative path, the
basename, or any parent directory (so `*.chd` matches at any depth, and a bare
`neogeocd` protects `neogeocd/...` just like `neogeocd/` does); a trailing `/`
applies recursively, globs included. When `--no-touch` is omitted,
`./notouch.txt` is used if it exists in the current directory.

With `--delete`, everything in the input directory except files matched by
`--no-touch` is deleted after successful archive creation; the input directory
itself is removed once it becomes empty (protected parent directories are kept
only while they still contain protected files). Add `--backup` to first copy the
untouched input directory to a sibling directory named
`INPUT_DIRECTORY.backup/`; it will not overwrite an existing backup.

`--output` defaults to `INPUT_DIRECTORY.zip` (or `.7z`) beside the input and
must point outside the input directory. `--no-lha-tag` extracts `.lha` files to
a directory without the default `-lha` suffix. If nothing remains after
exclusions, the program exits with `error: no files remain after exclusions`
and, without `--delete`, only the extracted contents are cleaned up.

Run `./batch_archive.py --help` for every option. The small regression check
can be run with `python3 test_batch_archive.py`.

Large directories are passed to the archiver in bounded argument batches, so
they do not hit the operating system command-line limit. ZIP preserves unusual
filenames; 7z rejects filenames containing a newline because 7z rewrites them.
