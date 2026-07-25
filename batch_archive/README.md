# batch_archive

Recursively extract ZIP, 7z, and LHA files, including nested archives, then create
one ZIP or 7z archive containing the extracted files rather than the source
archives. The default output is a sibling of the input directory, so it cannot
be added to or deleted from its own archive.

Requires Python 3 plus `unzip`, `zip`, and `lha` on `PATH`. On Arch Linux:

```bash
sudo pacman -S unzip zip lha
```

7z input or output also requires `7z` on `PATH`.

## Examples

Create the default ZIP beside `roms/` as `roms.zip`:

```bash
./batch_archive.py roms
```

Preview all extraction, archiving, and deletion commands without changing
files:

```bash
./batch_archive.py roms --test
```

Create a 7z archive at an explicit location:

```bash
./batch_archive.py roms --format 7z --output /archives/roms.7z
```

Archive the results, then remove the entire input directory after a successful
archive is created:

```bash
./batch_archive.py roms --delete
```

Keep selected files and archives unchanged while removing everything else:

```bash
./batch_archive.py roms --no-touch keep.txt --delete
```

LHA extractions go into `archive-lha/` by default so their origin remains
visible. Use `--no-lha-tag` to extract them into `archive/` instead.

For example, `keep.txt` can contain:

```gitignore
# Keep BIOS files and all save data.
bios/
*.sav

# Except this one save file.
!saves/newgame.sav
```

Without `--delete`, protected paths are still included in the final archive,
but are never extracted or deleted. Patterns are gitignore-like: blank lines and `#` comments
are ignored; `!` re-includes an earlier match; patterns containing `/` are
relative to the input directory; and a trailing `/` applies recursively. When
`--no-touch` is omitted, `./notouch.txt` is used if it exists in the current
directory.

With `--delete`, the whole input directory is removed after successful archive
creation; `--no-touch` is ignored. Add `--backup` to first copy the untouched
input directory to a sibling directory named `INPUT_DIRECTORY.backup/`; it will
not overwrite an existing backup.

Run `./batch_archive.py --help` for every option. The small regression check
can be run with `python3 test_batch_archive.py`.

Large directories are passed to the archiver in bounded argument batches, so
they do not hit the operating system command-line limit. ZIP preserves unusual
filenames; 7z rejects filenames containing a newline because 7z rewrites them.
