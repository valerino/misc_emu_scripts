#!/usr/bin/env python3
import argparse
import sys
import traceback
from pathlib import Path
import os
import re
from argparse import RawTextHelpFormatter


def create_gamelist(src, dst):
    print('[.] processing src=%s, dst=%s' % (src, dst))
    os.unlink(dst)

    with open(dst, 'w') as f:
        # write header
        f.write('<?xml version="1.0"?>\n')
        f.write('<gamelist>\n')

        # walk directory
        files = sorted(os.listdir(src))
        for game in files:
            _, ext = os.path.splitext(game)
            if ext.lower() == '.xml':
                continue
            if os.path.isdir(os.path.join(src, game)):
                continue

            # generate entry
            filename = Path(game).stem
            title = re.sub("\((.*?)\)", '', filename)

            f.write('<game>\n')
            f.write('\t<path>./%s</path>\n' % (filename))
            f.write('\t<name>%s</name>\n' % (title))
            f.write('\t<image>./boxart/%s.png</image>\n' % (title))
            f.write('\t<marquee>./wheel/%s.png</marquee>\n' % (title))
            f.write('\t<video>./boxart/%s.mp4</video>\n' % (title))
            f.write('</game>\n')

        # write footer
        f.write('</gamelist>\n')


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
