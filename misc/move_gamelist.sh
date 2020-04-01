#!zsh
# doesn't work with the default rpi shell, install zsh!

function sedeasy {
  sed -i "s/$(echo $1 | sed -e 's/\([[\/.*]\|\]\)/\\&/g')/$(echo $2 | sed -e 's/[\/&]/\\&/g')/g" $3
}

if [ -z "$1" ]; then    
    echo 'moves gamelist.xml and media from rpi .emulationstation to the roms folder, and fixes gamelist.xml paths'
    echo 'usage:' "$0" '<platform>'
    exit 1
fi

# check if exists
if [ ! -d "/home/pi/.emulationstation/gamelists/$1" ]; then
    echo '[x] error!' "/home/pi/.emulationstation/gamelists/$1" 'do not exists!'
    exit 1
fi
if [ ! -d "/home/pi/.emulationstation/downloaded_media/$1" ]; then
    echo '[w] warning!' "/home/pi/.emulationstation/downloaded_media/$1" 'do not exists!'
    exit 1
fi


# move
echo '. moving media to' "/home/pi/RetroPie/roms/$1/media"
mkdir -p "/home/pi/RetroPie/roms/$1/media"
mv "/home/pi/.emulationstation/downloaded_media/$1"/* "/home/pi/RetroPie/roms/$1/media"
if [ "$?" -eq 0 ]; then
    rm -rf "/home/pi/.emulationstation/downloaded_media/$1"   
fi

echo '. moving gamelist to' "/home/pi/RetroPie/roms/$1/gamelist.xml"
mv "/home/pi/.emulationstation/gamelists/$1"/* "/home/pi/RetroPie/roms/$1"    
if [ "$?" -eq 0 ]; then
    rm -rf "/home/pi/.emulationstation/gamelists/$1"
fi

# replace
echo '. fixing paths in' "/home/pi/RetroPie/roms/$1/gamelist.xml"
_old="/home/pi/RetroPie/roms/$1"
_new="."
sedeasy "$_old" "$_new" "/home/pi/RetroPie/roms/$1/gamelist.xml"
if [ "$?" -eq 0 ]; then
    _old="/home/pi/.emulationstation/downloaded_media/$1"
    _new="./media"
    sedeasy "$_old" "$_new" "/home/pi/RetroPie/roms/$1/gamelist.xml"
fi
echo '. done!'