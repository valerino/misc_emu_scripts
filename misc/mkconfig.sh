#!/usr/bin/env sh
# use with bash /path/to/mkoverlayconfig.sh on rpi

# examples
#
# default per-platform retroarch.cfg
# /opt/retropie/configs/dreamcast
# input_remapping_directory = "/opt/retropie/configs/dreamcast/"
# #include "/opt/retropie/configs/all/retroarch.cfg"
#
# game override
# ~/.config/retroarch/config/VecX/Tour\ De\ France\ \(USA\)\ \(Proto\).cfg
# input_overlay = "/media/usb0/retroarch/overlay-borders/1080 GCE Vectrex/Generic Vectrex Border/Tour_De_France_Proto.cfg"
#
# core override
# ~/.config/retroarch/config/VecX/VecX.cfg
# input_overlay = "/media/usb0/retroarch/overlay-borders/1080 GCE Vectrex/Generic Vectrex Border/border.cfg"

_CREATE_CORE_OVERRIDE_CFG=0
_CREATE_GAME_OVERRIDE_CFG=0
_CREATE_CONTENTDIR_OVERRIDE_CFG=0
_CREATE_RETROARCH_CFG=0
_OVERWRITE=0
_CONFIG_ROOT="$HOME/.config/retroarch/config"
declare -a _KEYS
declare -a _VALUES

function usage {
  echo 'create configuration for retropie\n'
  echo 'usage:' "$0" '\n\t-r -p <platform|all> -k <key> -v <value> [ -k <key> -v <value> ...] [-z config root instead of ~/.config/retroarch]\n\t\t[-w overwrite] to reset default retropie configuration for the given platform'
  echo '\t-g -c <path/to/game> -p <core> -k <key> -v <value> [ -k <key> -v <value> ...] [-z config root instead of ~/.config/retroarch]\n\t\t[-y /path/to/overlay shortcut to set overlay, ignores k/v pairs] [-w overwrite] to edit/create game override file'
  echo '\t-d -c <path/to/content_directory> -p <core> -k <key> -v <value> [ -k <key> -v <value> ...] [-z config root instead of ~/.config/retroarch]\n\t\t[-y /path/to/overlay shortcut to set overlay, ignores k/v pairs] [-w overwrite] to edit/create game override file'
  echo '\t-o -p <core> -k <key> -v <value> [ -k <key> -v <value> ...] [-z config root instead of ~/.config/retroarch]\n\t\t[-y /path/to/overlay shortcut to set overlay, ignores k/v pairs] [-w overwrite] to edit/create core override file\n'
}

function delete_line_starting_with_pattern {
  echo "[.] deleting lines starting with '$1' in '$2'"
  grep -v ^"$1 = " "$2" > tmp.txt
  cp ./tmp.txt "$2"
  rm ./tmp.txt
}

function check_overwrite {
  if [ -f "$1" ]; then
    if [ $_OVERWRITE -eq 1 ]; then
      echo "[.] overwriting: $1"
      rm "$1"
      return 1
    fi
  fi
  echo "[.] appending to: $1"
  return 0
}

function check_arrays {
  if [ ! -z $_OVERLAY ]; then
    echo "[.] setting overlay to "$_OVERLAY", no array checks."
    return 0
  fi

  _keycount=${#_KEYS[@]}
  _valcount=${#_VALUES[@]}
  
  if [ "$1" != "nocheckzero" ]; then
    if [ $_keycount -eq 0 ] && [ $_valcount -eq 0 ]; then
      echo '[x] ERROR: no keys/values provided.\n'
      return 1
    fi
  fi

  if [ $_keycount -ne $_valcount ]; then
    echo '[x] ERROR:' $_keycount '-k but' $_valcount '-v provided.\n'
    return 1
  fi
  return 0
}

while getopts "c:p:k:v:y:rowgd" arg; do
    case $arg in
        o)
          _CREATE_CORE_OVERRIDE_CFG=1
          ;;
        g)
          _CREATE_GAME_OVERRIDE_CFG=1
          ;;
        d)
          _CREATE_CONTENTDIR_OVERRIDE_CFG=1
          ;;
        r)
          _CREATE_RETROARCH_CFG=1
          ;;
        w)
          _OVERWRITE=1
          ;;
        p)
          _PLATFORM_CORE="${OPTARG}"
          ;;
        y)
          _OVERLAY="${OPTARG}"
          ;;
        Z)
          _CONFIG_ROOT="${OPTARG}"
          ;;
        c)
          _tmp="${OPTARG}"
          _tmp2=$(basename "$_tmp")
          _CFG_BASEDIR=$(dirname "${OPTARG}/dummy")
          _CFG_BASENAME=$(echo "$_tmp2" | rev | cut -c 5- | rev).cfg
          ;;
        k)
          _KEYS+=("${OPTARG}")
          ;;
        v)
          _VALUES+=("${OPTARG}")
          ;;
        *)
          usage
          exit 1
          ;;
    esac
done

# check params
if [ $_CREATE_RETROARCH_CFG -eq 1 ]; then
  if [ -z "$_PLATFORM_CORE" ]; then
    usage
    exit 1
  fi

  # check if keys and values are balanced
  check_arrays nocheckzero
  if [ $? -ne 0 ]; then
    usage
    exit 1
  fi

  if [ "$_PLATFORM_CORE" = "all" ]; then
    # no overwrite here
    _OVERWRITE=0
    echo '[.] platform "all", overwrite forced to disabled.'
  fi

  # params ok
  echo '[.] editing retroarch.cfg for platform' "$_PLATFORM_CORE"
  _CFG="/opt/retropie/configs/$_PLATFORM_CORE/retroarch.cfg"

elif [ $_CREATE_CONTENTDIR_OVERRIDE_CFG -eq 1 ] || [ $_CREATE_GAME_OVERRIDE_CFG -eq 1 ]; then
  if [ -z "$_CFG_PATH" ] && [ -z "$_PLATFORM_CORE" ]; then
    usage
    exit 1
  fi
  # check if keys and values are balanced
  check_arrays
  if [ $? -ne 0 ]; then
    usage
    exit 1
  fi

  # params ok
  _CFG="$_CONFIG_ROOT/$_PLATFORM_CORE/$_CFG_BASENAME"
  if [ $_CREATE_CONTENTDIR_OVERRIDE_CFG -eq 1 ]; then
    echo '[.] editing content directory override:' "$_CFG"
    _CFG="$_CONFIG_ROOT/$_PLATFORM_CORE/$_CFG_BASEDIR"
  else
    echo '[.] editing game override:' "$_CFG"
    _CFG="$_CONFIG_ROOT/$_PLATFORM_CORE/$_CFG_BASENAME"
  fi

elif [ $_CREATE_CORE_OVERRIDE_CFG -eq 1 ]; then
  if [ -z "$_PLATFORM_CORE" ]; then
    usage
    exit 1
  fi

  # check if keys and values are balanced
  check_arrays
  if [ $? -ne 0 ]; then
    usage
    exit 1
  fi

  # params ok
  _CFG="$_CONFIG_ROOT/$_PLATFORM_CORE/$_PLATFORM_CORE.cfg"
  echo '[.] editing core override:' "$_CFG"

else
  # wrong params
  usage
  exit 1
fi

_DIRNAME=$(dirname "$_CFG")
if [ $_CREATE_RETROARCH_CFG -eq 1 ]; then
  # editing retroarch cfg
  _keycount=${#_KEYS[@]}
  check_overwrite "$_CFG"
  mkdir -p "$_DIRNAME"
  if [ "$_keycount" -eq 0 ]; then
    # create default
    _str="input_remapping_directory = \"/opt/retropie/configs/$_PLATFORM_CORE/\""
    echo "$_str" >> "$_CFG"
    _str="#include \"/opt/retropie/configs/all/retroarch.cfg\""
    echo "$_str" >> "$_CFG"
  else
    # edit
    for ((_i = 0; _i < $_keycount; _i++)); do
      delete_line_starting_with_pattern ${_KEYS[$_i]} "$_CFG"
      _str="${_KEYS[$_i]} = \"${_VALUES[$_i]}\""
      echo "$_str" >> "$_CFG"
    done
  fi
else
  # everything else
  check_overwrite "$_CFG"
  mkdir -p "$_DIRNAME"
  if [ -z "$_OVERLAY" ]; then 
    # use arrays
    for ((_i = 0; _i < $_keycount; _i++)); do
      delete_line_starting_with_pattern ${_KEYS[$_i]} "$_CFG"
      _str="${_KEYS[$_i]} = \"${_VALUES[$_i]}\""
      echo "$_str" >> "$_CFG"
    done
  else
    # shortcut to set overlay
      delete_line_starting_with_pattern "input_overlay = " "$_CFG"
      _str="input_overlay = \"$_OVERLAY\""
      echo "$_str" >> "$_CFG"
  fi
fi

echo '[.] DONE, written' "$_CFG" '!'
