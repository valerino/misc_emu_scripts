#!/usr/bin/env python3

import argparse
import sys
import traceback
from pathlib import Path
import os
import re
from argparse import RawTextHelpFormatter
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement
import xml.dom.minidom


def create_gamelist(src, dst):
    print('[.] processing src=%s, dst=%s' % (src, dst))
    try:
        os.unlink(dst)
    except:
        pass

    gamelist = Element('gameList')

    # walk directory
    files = sorted(os.listdir(src))
    for g in files:
        # skip unwanted
        _, ext = os.path.splitext(g)
        if ext.lower() == '.xml' or ext.lower() == '.srm' or ext.lower() == '.nvr' or ext.lower == '.ds_store':
            continue
        if os.path.isdir(os.path.join(src, g)):
            continue

        # generate entry
        game = SubElement(gamelist, 'game')
        title = Path(g).stem

        path = SubElement(game, 'path')
        path.text = './%s' % (g)

        name = SubElement(game, 'name')
        name.text = title

        image = SubElement(game, 'image')
        image.text = './boxart/%s.png' % (title)

        marquee = SubElement(game, 'marquee')
        marquee.text = './wheel/%s.png' % (title)

        video = SubElement(game, 'video')
        video.text = './snap/%s.mp4' % (title)

    # done, write to file
    ss = ET.tostring(gamelist, 'utf-8')
    s = xml.dom.minidom.parseString(ss).toprettyxml(indent='\t')
    with open(dst, 'w') as f:
        f.write(s)


def main():
    d = "generates basic gamelist.xml for a folder, with images/snaps/wheel pointing to ./boxart, ./snap, ,/wheel."

    parser = argparse.ArgumentParser(
        description=d, formatter_class=RawTextHelpFormatter)

    parser.add_argument('--src', help='path to create gamelist into',
                        nargs=1, required=True)
    parser.add_argument('--dst', help='optional destination gamelist.xml (default is path at --src/gamelist.xml)',
                        nargs=1, default=None)
    args = parser.parse_args()
    try:

        if args.dst is None:
            dst = "%s/gamelist.xml" % (args.src[0])
        else:
            dst = args.dst[0]

        create_gamelist(args.src[0], dst)
        print('[.] Done, written %s !' % (dst))
    except Exception as ex:
        # error
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
