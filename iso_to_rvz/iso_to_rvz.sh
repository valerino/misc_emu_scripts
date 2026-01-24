#!/usr/bin/env bash

function usage {
    echo 'convert .iso (or archives containing .iso) to .rvz using dolphin-tool\n'
    echo 'usage:' "$1" '-p <path/to/folder|path/to/file> [-o <output/folder>] [-t to test run] [-d to delete source files after success] [-z to use 7z for decompression (default unzip)] [-s to scrub junk data] [-f <format> to specify output format (rvz, gcz, wia, iso)] [-l <level> to specify compression level (0-22)]\n'
}

_TEST_RUN=0
_DELETE_SRC=0
_USE_7Z=0
_SCRUB=0
_FORMAT="rvz"
_COMP_LEVEL=5
_PATH=""
_OUTDIR=""

while getopts "tp:do:zsf:l:" arg; do
    case $arg in
        p)
            _PATH="${OPTARG}"
            ;;
        o)
            _OUTDIR="${OPTARG}"
            ;;
        t)
            _TEST_RUN=1
            ;;
        d)
            _DELETE_SRC=1
            ;;
        z)
            _USE_7Z=1
            ;;
        s)
            _SCRUB=1
            ;;
        f)
            _FORMAT="${OPTARG}"
            ;;
        l)
            _COMP_LEVEL="${OPTARG}"
            ;;
        *)
            usage "$0"
            exit 1
            ;;
    esac
done

# validate format
_FORMAT=$(echo "$_FORMAT" | tr '[:upper:]' '[:lower:]')
if ! echo "$_FORMAT" | grep -qE "^(rvz|gcz|wia|iso)$"; then
  echo "[x] unsupported format: $_FORMAT. Supported formats: rvz, gcz, wia, iso"
  exit 1
fi

# validate compression level (integer, reasonable range 0-22)
if ! echo "$_COMP_LEVEL" | grep -qE '^[0-9]+$'; then
  echo "[x] invalid compression level: $_COMP_LEVEL (must be an integer)"
  exit 1
fi
if [ "$_COMP_LEVEL" -lt 0 ] || [ "$_COMP_LEVEL" -gt 22 ]; then
  echo "[x] compression level out of range: $_COMP_LEVEL (valid: 0-22)"
  exit 1
fi

if [ "$_PATH" == "" ]; then
  usage "$0"
  exit 1
fi

# check dolphin-tool exists
if ! command -v dolphin-tool >/dev/null 2>&1; then
  echo "[x] dolphin-tool not found in PATH. Please install it."
  exit 1
fi

# check unzip/7z based on option
if [ $_USE_7Z -eq 1 ]; then
  if ! command -v 7z >/dev/null 2>&1; then
    echo "[x] 7z not found in PATH but -z specified. Install p7zip-full."
    exit 1
  fi
else
  if ! command -v unzip >/dev/null 2>&1; then
    echo "[x] unzip not found in PATH. Install unzip or use -z to use 7z."
    exit 1
  fi
fi

# determine default output directory if not provided
if [ "$_OUTDIR" == "" ]; then
  if [ -f "$_PATH" ]; then
    _OUTDIR=$(dirname "$_PATH")
  else
    _OUTDIR="$_PATH"
  fi
fi

# create output dir if needed (skip in test mode)
if [ $_TEST_RUN -eq 0 ]; then
  mkdir -p "$_OUTDIR"
else
  echo "[.] (test) output directory would be: $_OUTDIR"
fi

# print chosen parameters so the user can verify what's being used
echo "[.] settings:"
echo "    input: $_PATH"
echo "    output: $_OUTDIR"
echo "    test mode: $( [ $_TEST_RUN -eq 1 ] && echo yes || echo no )"
echo "    delete input on success: $( [ $_DELETE_SRC -eq 1 ] && echo yes || echo no )"
echo "    use 7z for extraction: $( [ $_USE_7Z -eq 1 ] && echo yes || echo no )"
echo "    scrub enabled: $( [ $_SCRUB -eq 1 ] && echo yes || echo no )"
echo "    format: $_FORMAT"
echo "    compression level: $_COMP_LEVEL"

echo "[.] processing $_PATH -> $_OUTDIR"

# If _PATH is a file, process it directly; otherwise search the directory
rm -f /tmp/isos_to_rvz.txt
if [ -f "$_PATH" ]; then
  # single file input
  _file_lower=$(echo "$_PATH" | awk '{print tolower($0)}')
  if echo "$_file_lower" | grep -qE "\.(iso|zip|7z)$"; then
    echo "$_PATH" > /tmp/isos_to_rvz.txt
  else
    echo "[x] input file '$_PATH' is not a supported type (.iso, .zip, .7z)"
    exit 1
  fi
elif [ -d "$_PATH" ]; then
  find "$_PATH" -type f \( -iname "*.zip" -o -iname "*.7z" -o -iname "*.iso" \) > /tmp/isos_to_rvz.txt
  if [ $? -ne 0 ]; then
    echo "[x] wrong input, or problem scanning directory"
    rm -f /tmp/isos_to_rvz.txt
    exit 1
  fi
else
  echo "[x] '$_PATH' is neither a file nor a directory"
  exit 1
fi

if [ ! -s /tmp/isos_to_rvz.txt ]; then
  echo "[x] no matching files found in '$_PATH'"
  rm -f /tmp/isos_to_rvz.txt
  exit 1
fi

while IFS= read -r file; do
  if [ -d "$file" ]; then
    continue
  fi

  ext=$(echo "$file" | rev | cut -d'.' -f1 | rev | tr '[:upper:]' '[:lower:]')

  tmpdir=$(mktemp -d -t iso_to_rvz.XXXX)
  extracted_isos=()

  if [ "$ext" == "iso" ]; then
    extracted_isos+=("$file")
    src_is_archive=0
  else
    # attempt to extract .iso files
    if [ $_USE_7Z -eq 1 ]; then
      if [ $_TEST_RUN -eq 1 ]; then
        echo "[.] (test) listing (7z) archive contents for .iso: $file"
        # list files inside archive and filter for .iso entries
        isonames=$(7z l -ba "$file" 2>/dev/null | awk '{print $NF}' | grep -i -E '\\.iso$' || true)
        if [ "$isonames" == "" ]; then
          echo "    (test) no .iso entries found in archive"
        else
          echo "    (test) found .iso entries:"
          echo "$isonames" | while IFS= read -r n; do
            echo "    (test) would convert: $n -> $_OUTDIR/${n%.*}.rvz"
          done
        fi
      else
        echo "[.] extracting (7z): $file -> $tmpdir"
        7z e -y -o"$tmpdir" "$file" "*.iso" >/dev/null 2>&1
      fi
    else
      if [ $_TEST_RUN -eq 1 ]; then
        echo "[.] (test) listing (zip) archive contents for .iso: $file"
        if command -v unzip >/dev/null 2>&1; then
          isonames=$(unzip -Z1 "$file" 2>/dev/null | grep -i -E '\\.iso$' || true)
        else
          isonames=$(unzip -l "$file" 2>/dev/null | awk '{print $4}' | grep -i -E '\\.iso$' || true)
        fi
        if [ "$isonames" == "" ]; then
          echo "    (test) no .iso entries found in archive"
        else
          echo "    (test) found .iso entries:"
          echo "$isonames" | while IFS= read -r n; do
            echo "    (test) would convert: $n -> $_OUTDIR/${n%.*}.rvz"
          done
        fi
      else
        echo "[.] extracting (unzip): $file -> $tmpdir"
        unzip -j -o "$file" "*.iso" -d "$tmpdir" >/dev/null 2>&1 || true
      fi
    fi

    # collect extracted isos (only when not test run)
    if [ $_TEST_RUN -eq 0 ]; then
      while IFS= read -r iso; do
        extracted_isos+=("$iso")
      done < <(find "$tmpdir" -maxdepth 1 -type f -iname "*.iso")
    fi

    src_is_archive=1
  fi

  if [ ${#extracted_isos[@]} -eq 0 ]; then
    echo "[!] no .iso found for: $file -- skipping"
    rm -rf "$tmpdir"
    continue
  fi

  total_isos=${#extracted_isos[@]}
  success_count=0

  for iso in "${extracted_isos[@]}"; do
    base=$(basename "$iso")
    name="${base%.*}"
    outpath="$_OUTDIR/$name.rvz"

    # add scrub argument if requested
    DOLPHIN_SCRUB_ARG=""
    if [ $_SCRUB -eq 1 ]; then
      DOLPHIN_SCRUB_ARG="-s"
    fi

    if [ $_TEST_RUN -eq 1 ]; then
      echo "[.] (test) would convert: $iso -> $outpath"
      echo "    (test) dolphin-tool convert -i \"$iso\" -o \"$outpath\" $DOLPHIN_SCRUB_ARG -f \"$_FORMAT\" -b 131072 -c zstd -l $_COMP_LEVEL"
      success=0
    else
      echo "[.] converting: $iso -> $outpath"
      dolphin-tool convert -i "$iso" -o "$outpath" $DOLPHIN_SCRUB_ARG -f "$_FORMAT" -b 131072 -c zstd -l $_COMP_LEVEL
      success=$?
    fi

    if [ $success -ne 0 ]; then
      echo "[x] conversion failed for $iso"
      # continue to next iso
    else
      # In non-test runs, verify output exists and is non-empty before treating as success
      if [ $_TEST_RUN -eq 0 ]; then
        if [ ! -f "$outpath" ] || [ ! -s "$outpath" ]; then
          echo "[x] conversion reported success but output missing or empty: $outpath"
          echo "[x] conversion failed for $iso"
          success=1
          # don't delete source
          continue
        fi
      fi

      echo "[✓] converted: $outpath"
      success_count=$((success_count+1))

      # delete source iso (if it was a standalone iso)
      if [ $src_is_archive -eq 0 ]; then
        if [ $_DELETE_SRC -eq 1 ]; then
          if [ $_TEST_RUN -eq 1 ]; then
            echo "[.] (test) would delete iso: $iso"
          else
            echo "[.] deleting iso: $iso"
            rm -f "$iso"
          fi
        fi
      else
        # if it came from an archive, remove the extracted iso file only
        if [ $_TEST_RUN -eq 1 ]; then
          echo "[.] (test) would remove extracted iso: $iso"
        else
          rm -f "$iso" 2>/dev/null || true
        fi
      fi
    fi
  done

  # after all extracted ISOs were attempted, handle archive deletion if requested
  if [ $src_is_archive -eq 1 ]; then
    if [ $success_count -eq $total_isos ]; then
      if [ $_DELETE_SRC -eq 1 ]; then
        if [ $_TEST_RUN -eq 1 ]; then
          echo "[.] (test) would delete archive: $file (all $success_count/$total_isos succeeded)"
        else
          echo "[.] deleting archive: $file (all $success_count/$total_isos succeeded)"
          rm -f "$file"
        fi
      fi
    else
      echo "[!] not deleting archive: $file (only $success_count/$total_isos succeeded)"
    fi
  fi

  rm -rf "$tmpdir"

done < /tmp/isos_to_rvz.txt
rm -f /tmp/isos_to_rvz.txt

echo '[.] done!'
