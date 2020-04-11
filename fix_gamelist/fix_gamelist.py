#!/usr/bin/env python3

import argparse
import sys
import traceback
import xml.etree.ElementTree as ET
import os
import glob
from argparse import RawTextHelpFormatter


def is_missing(name, t, s):
    """
    @return true if the entry is missing (desc is missing or path to game/cover/image is missing)
    """
    missing = False
    if s == None or len(s) == 0:
        # path/image/cover/desc not defined
        missing = True

    if t == 'path' or t == 'image' or t == 'cover':
        # check if file exists
        if s is not None and not os.path.exists(s):
            # print('[w] entry=%s, %s not found!' % (name, s))
            missing = True

    if missing:
        # print('[w] entry=%s, %s is missing!' % (name, t))
        return True

    # exists and valid
    return False


def process_m3us(xml, out, fix_m3u_folder):
    # read input xml
    tree = ET.parse(xml)
    root = tree.getroot()
    games = root.findall('game')

    # get all m3u files in the given folder
    files = glob.glob(os.path.join(fix_m3u_folder, '*.m3u'))
    for f in files:
        # read m3u line by line
        print('[.] parsing m3u: %s' % f)
        with open(f) as m3u:
            for cnt, line in enumerate(m3u):
                # for each line, patch gamelist
                line = line.rstrip().lower()
                for game in games:
                    try:
                        path = game.find('path').text
                    except:
                        path = None

                    a = os.path.basename(path.lower())
                    b = os.path.basename(line)
                    if a == b:
                        # remove this entry
                        print(
                            '[.] DELETED entry with path=%s (already in m3u=%s)' % (path, f))
                        root.remove(game)
    # done, rewrite xml
    tree.write(out)


def process_gamelist(xml, out, check_path, check_image, check_cover, check_desc, interactive, delete_files, alt, alt2, fixm3u_folder):
    print('[.] processing IN=%s, OUT=%s, check_path=%r, check_image=%r, check_cover=%r, check_desc=%r, interactive=%r, delete_files=%r, alt=%r, alt2=%r, fixm3u_folder=%s)' %
          (xml, out, check_path, check_image, check_cover, check_desc, interactive, delete_files, alt, alt2, fixm3u_folder))

    if fixm3u_folder:
        # fix gamelist for m3us
        return process_m3us(xml, out, fixm3u_folder)

    # read xml
    tree = ET.parse(xml)
    root = tree.getroot()

    # cycle games
    games = root.findall('game')
    for game in games:
        try:
            path = game.find('path').text
        except:
            path = None

        try:
            name = game.find('name').text
        except:
            name = None

        try:
            image = game.find('image').text
        except:
            image = None

        try:
            cover = game.find('cover').text
        except:
            cover = None

        try:
            desc = game.find('desc').text
        except:
            desc = None

        # initialize to no remove, has everything
        remove = False
        has_path = True
        has_cover = True
        has_image = True
        has_desc = True

        missing = is_missing(name, 'path', path)
        if missing:
            # path is missing, can be removed
            has_path = False
            if check_path:
                remove = True

        missing = is_missing(name, 'image', image)
        if missing:
            # image is missing, can be removed
            has_image = False
            if check_image:
                remove = True

        missing = is_missing(name, 'cover', cover)
        if missing:
            # cover is missing, can be removed
            has_cover = False
            if check_cover:
                remove = True

        missing = is_missing(name, 'desc', desc)
        if missing:
            # desc is missing, can be removed
            has_desc = False
            if check_desc:
                remove = True

        # now check the alt flags if any
        if alt:
            if has_path and (has_cover or has_image):
                # do not remove anyway
                remove = False
        if alt2:
            if has_path and (has_cover or has_image or has_desc):
                # do not remove anyway
                remove = False

        # ok, now remove (asking if --interactive was specified)
        if interactive:
            if remove:
                k = input('[?] OK TO DELETE entry=%s (has_path=%r, has_image=%r, has_cover=%r, has_desc=%r) ? [Y/n] ' %
                          (name, has_path, has_image, has_cover, has_desc))
                if k.lower() == 'n':
                    remove = False

        if remove:
            # delete xml entry
            print('[.] DELETED entry=%s (has_path=%r, has_image=%r, has_cover=%r, has_desc=%r)' %
                  (name, has_path, has_image, has_cover, has_desc))
            root.remove(game)
        if delete_files:
            # also delete files
            if has_path:
                os.unlink(path)
            if has_image:
                os.unlink(image)
            if has_cover:
                os.unlink(cover)

    # done, rewrite xml
    tree.write(out)
    return 0


def main():
    d = """cleanup gamelist.xml, for EmulationStation et al.\n
    by specifying --check_path, --check_image, --check_cover it will check entry path/image/cover tags and their associated filepath.
    by specifying --check_desc, it will check also for missing game description.
    if any of these check is specified and fails, the entry is flagged to be removed.

    all the check_flags are ignored if one of the --alt or --alt2 flags is specified:

    by specifying --alt, an entry is kept only if path and the associated file exists AND at least one image/cover exists.
    by specifying --alt2, an entry is kept only if path and the associated file exists AND at least one image/cover/desc exists.
    
    if --fix_m3u (or --fix_m3u_from_input) is specified, all flags are ignored and the given folder is scanned for .m3u : for each .m3u it finds 
    in this folder, it deletes the duplicated entries (paths specified inside the .m3u) from the input gamelist.xml.
    """

    parser = argparse.ArgumentParser(
        description=d, formatter_class=RawTextHelpFormatter)

    parser.add_argument('--xml', help='source gamelist.xml',
                        nargs=1, required=True)
    parser.add_argument('--out', help='destination gamelist.xml (default overwrites)',
                        nargs=1, default=None)
    parser.add_argument('--interactive', help='ask confirmation before removing an entry',
                        action='store_const', const=True, default=False)
    parser.add_argument("--check_path", help='remove entries with missing "path" tag or file',
                        action='store_const', const=True, default=False)
    parser.add_argument("--check_image", help='remove entries with missing "image" tag or file',
                        action='store_const', const=True, default=False)
    parser.add_argument("--check_cover", help='remove entries with missing "cover" tag or file',
                        action='store_const', const=True, default=False)
    parser.add_argument("--check_desc", help='remove entries with missing "desc" tag or content',
                        action='store_const', const=True, default=False)
    parser.add_argument("--alt", help='all check_* flags are ignored, an entry is kept only if path exist AND at least one image/cover exists',
                        action='store_const', const=True, default=False)
    parser.add_argument("--alt2", help='all check_* flags are ignored, an entry is kept only if path exist AND at least one image/cover/desc exists',
                        action='store_const', const=True, default=False)
    parser.add_argument("--delete_files", help='remove also files associated with path/image/cover when removing the entry',
                        action='store_const', const=True, default=False)
    parser.add_argument("--fix_m3u", help='path to a folder to scan for .m3u and the inputgamelist.xml paths are fixed accordingly.',
                        nargs=1, default=None)
    parser.add_argument("--fix_m3u_from_input", help='input gamelist parent folder is scanned for *.m3u and the input gamelist.xml paths are fixed accordingly.',
                        action='store_const', const=True, default=False)
    args = parser.parse_args()
    try:
        if args.alt and args.alt2:
            raise Exception('--alt and --alt2 are mutually exclusive!')

        if args.fix_m3u_from_input and (args.fix_m3u is not None):
            raise Exception(
                '--fix_m3u and --fix_m3u_from_input are mutually exclusive!')

        fix_m3u_folder = args.fix_m3u[0] if args.fix_m3u else None
        if args.fix_m3u_from_input:
            fix_m3u_folder = os.path.dirname(args.xml[0])
        process_gamelist(args.xml[0], args.out[0] if args.out else args.xml[0], args.check_path, args.check_image,
                         args.check_cover, args.check_desc, args.interactive, args.delete_files, args.alt, args.alt2,
                         fix_m3u_folder)
        print('[.] Done, written %s !' %
              args.out[0] if args.out else args.xml[0])
    except Exception as ex:
        # error
        traceback.print_exc()
        return 1

    finally:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
