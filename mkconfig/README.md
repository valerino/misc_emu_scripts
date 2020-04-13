# mkconfig

easily create/edit retroarch/retropie configurations automatically from commandline (in retropie directly) !

usage: 

~~~bash
create configuration for retropie

usage: ./mkconfig/mkconfig.sh 
        -r -p <platform|all> -k <key> -v <value> [ -k <key> -v <value> ...] [-z config root instead of ~/.config/retroarch]
                [-y /path/to/overlay shortcut to set overlay, ignores k/v pairs]
                [-x path/to/config use this config as base] [-w overwrite] to reset default retropie configuration for the given platform
        -g -c <path/to/game> -p <core> -k <key> -v <value> [ -k <key> -v <value> ...] [-z config root instead of ~/.config/retroarch]
                [-y /path/to/overlay shortcut to set overlay, ignores k/v pairs]
                [-x path/to/config use this config as base] [-w overwrite] to edit/create game override file
        -d -c <path/to/content_directory> -p <core> -k <key> -v <value> [ -k <key> -v <value> ...] [-z config root instead of ~/.config/retroarch]
                [-y /path/to/overlay shortcut to set overlay, ignores k/v pairs]
                [-x path/to/config use this config as base] [-w overwrite] to edit/create game override file
        -o -p <core> -k <key> -v <value> [ -k <key> -v <value> ...] [-z config root instead of ~/.config/retroarch]
                [-y /path/to/overlay shortcut to set overlay, ignores k/v pairs]
                [-x path/to/config use this config as base] [-w overwrite] to edit/create core override file
~~~

sample usage:

~~~bash
# create/reset default configuration for amiga
/media/usb0/retroarch » bash ~/mkconfig.sh -r -p amiga -w
[.] editing retroarch.cfg for platform amiga
[.] overwriting: /opt/retropie/configs/amiga/retroarch.cfg
[.] creating default configuration for platform amiga
[.] DONE, written /opt/retropie/configs/amiga/retroarch.cfg !

# set overlay for amiga
/media/usb0/retroarch » bash ~/mkconfig.sh -r -p amiga -y ~/.config/configroot/overlay/retroarch-overlays/Commodore-Amiga-Bezel-16x9-2560x1440.cfg
[.] setting overlay to /home/pi/.config/configroot/overlay/retroarch-overlays/Commodore-Amiga-Bezel-16x9-2560x1440.cfg, no array checks.
[.] editing retroarch.cfg for platform amiga
[.] appending to: /opt/retropie/configs/amiga/retroarch.cfg
[.] deleting lines starting with 'input_overlay = ' in '/opt/retropie/configs/amiga/retroarch.cfg'
[.] DONE, written /opt/retropie/configs/amiga/retroarch.cfg !

# same as above, one shot (useful to reset and set overlay together)
/media/usb0/retroarch » bash ~/mkconfig.sh -r -w -p amiga -y ~/.config/configroot/overlay/retroarch-overlays/Commodore-Amiga-Bezel-16x9-2560x1440.cfg

# same as above, specify keys manually (-k and -v can be specified multiple times to edit more keys)
/media/usb0/retroarch » bash ~/mkconfig.sh -r -w -p amiga -k input_overlay -v ~/.config/configroot/overlay/retroarch-overlays/Commodore-Amiga-Bezel-16x9-2560x1440.cfg

# check created configuration
/media/usb0/retroarch » cat /opt/retropie/configs/amiga/retroarch.cfg
input_remapping_directory = "/opt/retropie/configs/amiga/"
#include "/opt/retropie/configs/all/retroarch.cfg"
input_overlay = "/home/pi/.config/configroot/overlay/retroarch-overlays/Commodore-Amiga-Bezel-16x9-2560x1440.cfg"
~~~

~~~bash
# create game override (i.e. vectrex)
/media/usb0/retroarch » bash ~/mkconfig.sh -g -p VecX -c /home/pi/RetroPie/roms/vectrex/3D\ Crazy\ Coaster\ \(USA\).zip -y /media/usb0/retroarch/overlay/overlay-borders/1080\ GCE\ Vectrex/Generic\ Vectrex\ Border/3D_Crazy_Coaster.cfg -w
~~~
