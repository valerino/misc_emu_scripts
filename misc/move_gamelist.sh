#!/usr/bin/env bash
# use with bash /path/to/move_gamelist.sh on rpi

function sed_wrapper {
  sed -i "s/$(echo $1 | sed -e 's/\([[\/.*]\|\]\)/\\&/g')/$(echo $2 | sed -e 's/[\/&]/\\&/g')/g" $3
}

function usage {
    echo 'moves gamelist.xml and media from rpi .emulationstation to the roms folder, and put relative paths in gamelist.xml'
    echo 'usage:' "$0" '<platform> <--media|--images to use .emulationstation/downloaded_media or .emulationstation/downloaded_images>'
}

if [ "$#" -ne 2 ]; then
    usage "$0"    
    exit 1
fi

# check if directories exists
if [ ! -d "/home/pi/.emulationstation/gamelists/$1" ]; then
    echo '[x] error!' "/home/pi/.emulationstation/gamelists/$1" 'do not exists!'
    exit 1
fi
if [ "$2" = '--media' ]; then
    if [ ! -d "/home/pi/.emulationstation/downloaded_media/$1" ]; then
        echo '[w] warning!' "/home/pi/.emulationstation/downloaded_media/$1" 'do not exists!'
        exit 1
    fi
elif [ "$2" = '--images' ]; then
    if [ ! -d "/home/pi/.emulationstation/downloaded_images/$1" ]; then
        echo '[w] warning!' "/home/pi/.emulationstation/downloaded_media/$1" 'do not exists!'
        exit 1
    fi
else
    usage "$0"
    exit 1
fi

# move
echo '. moving gamelist to' "/home/pi/RetroPie/roms/$1/gamelist.xml"
mv "/home/pi/.emulationstation/gamelists/$1"/* "/home/pi/RetroPie/roms/$1"    
if [ "$?" -eq 0 ]; then
    rm -rf "/home/pi/.emulationstation/gamelists/$1"
fi

if [ "$2" = '--media' ]; then
    echo '. moving media to' "/home/pi/RetroPie/roms/$1/media"
    mkdir -p "/home/pi/RetroPie/roms/$1/media"
    mv "/home/pi/.emulationstation/downloaded_media/$1"/* "/home/pi/RetroPie/roms/$1/media"
    if [ "$?" -eq 0 ]; then
        rm -rf "/home/pi/.emulationstation/downloaded_media/$1"   
    fi
else
    echo '. moving images to' "/home/pi/RetroPie/roms/$1/media"
    mkdir -p "/home/pi/RetroPie/roms/$1/media/snap"
    mv "/home/pi/.emulationstation/downloaded_images/$1"/* "/home/pi/RetroPie/roms/$1/media/snap"
    if [ "$?" -eq 0 ]; then
        rm -rf "/home/pi/.emulationstation/downloaded_images/$1"   
    fi
fi

# replace
echo '. fixing paths in' "/home/pi/RetroPie/roms/$1/gamelist.xml"
if [ "$2" = '--media' ]; then
    _old="/home/pi/RetroPie/roms/$1"
    _new="."
    sed_wrapper "$_old" "$_new" "/home/pi/RetroPie/roms/$1/gamelist.xml"
    if [ "$?" -eq 0 ]; then
        _old="/home/pi/.emulationstation/downloaded_media/$1"
        _new="./media"
        sed_wrapper "$_old" "$_new" "/home/pi/RetroPie/roms/$1/gamelist.xml"
        _old="~/.emulationstation/downloaded_media/$1"
        _new="./media"
        sed_wrapper "$_old" "$_new" "/home/pi/RetroPie/roms/$1/gamelist.xml"
    fi
else
    _old="/home/pi/RetroPie/roms/$1"
    _new="."
    sed_wrapper "$_old" "$_new" "/home/pi/RetroPie/roms/$1/gamelist.xml"
    if [ "$?" -eq 0 ]; then
        _old="/home/pi/.emulationstation/downloaded_images/$1"
        _new="./media/snap"
        sed_wrapper "$_old" "$_new" "/home/pi/RetroPie/roms/$1/gamelist.xml"
        _old="~/.emulationstation/downloaded_images/$1"
        _new="./media/snap"
        sed_wrapper "$_old" "$_new" "/home/pi/RetroPie/roms/$1/gamelist.xml"
    fi
fi

echo '. done!'