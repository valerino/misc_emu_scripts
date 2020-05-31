#!/usr/bin/env python3

import argparse
import sys
import traceback
import os
import re
import shutil
from argparse import RawTextHelpFormatter
import subprocess


def skip(to_skip, dstdir, delskipped, test):
    """
    move file to dstdir/skipped, or just delete
    """
    if delskipped:
        print('[.] DELETING skipped file: %s' % (to_skip))
        if not test:
            os.unlink(to_skip)
        return

    # move skipped
    skipped_dir = os.path.join(dstdir, 'skipped')
    skipped_path = os.path.join(skipped_dir, os.path.basename(to_skip))
    os.makedirs(skipped_dir, exist_ok=True)
    print('[.] SKIPPING %s, moving to %s' % (to_skip, skipped_path))
    if not test:
        shutil.move(to_skip, skipped_path)


def del_file(path, test):
    """
    delete file at path
    """
    if not test:
        os.unlink(path)


def unar(to_unar, dstdir, delarchives, test):
    """
    unarchive file to dstdir
    """
    print('[.] extracting %s to %s' % (to_unar, dstdir))
    if not test:
        subprocess.run(['unar', '-f', '-o', dstdir, to_unar])
    if delarchives == True:
        print('[.] deleting archive: %s' % (to_unar))
        del_file(to_unar, test)


def copy_file(src, dstdir, test):
    """
    copy file to dstdir
    @return dstpath
    """
    dstpath = os.path.join(dstdir, os.path.basename(src))
    if dstpath == src:
        # overlap, break
        return dstpath

    print('[.] copying %s to %s' % (src, dstpath))
    if not test:
        os.makedirs(dstdir, exist_ok=True)
        shutil.copy(src, dstpath)

    return dstpath


def move_file(src, dstdir, test):
    """
    move file to dstdir
    @return dstpath
    """
    dstpath = os.path.join(dstdir, os.path.basename(src))
    if dstpath == src:
        # overlap, break
        return dstpath

    print('[.] moving %s to %s' % (src, dstpath))
    if not test:
        os.makedirs(dstdir, exist_ok=True)
        shutil.move(src, dstpath)

    return dstpath


def is_bad(file):
    m = re.match('.+\[b\d*]', file, re.I)
    if m:
        return True

    return False


def is_alt(file):
    m = re.match('.+\[a\d*]', file, re.I)
    if m:
        return True

    return False


def dec_alphadir(file, alphadirs):
    barename = os.path.basename(file)
    firstletter = barename.upper()[0]
    if not firstletter.isalpha():
        firstletter = '#'

    try:
        n = alphadirs[firstletter]
        n -= 1
    except Exception as ex:
        n = 0

    # update
    alphadirs[firstletter] = n


def get_dest_alpha_dir(file, dst, alphadirs):
    """
    get destinetion alpha directory for file
    """
    barename = os.path.basename(file)
    firstletter = barename.upper()[0]
    if not firstletter.isalpha():
        firstletter = '#'

    try:
        n = alphadirs[firstletter]
    except Exception as ex:
        n = 0

    # numbered (A1,A2,A3, ....)
    dirn = n // 255
    dstdir = os.path.join(dst, firstletter + str(dirn))

    # update
    n += 1
    alphadirs[firstletter] = n
    return dstdir


def do_moveunalpha(src, dst, test):
    """
    assumes src is alpha folders, just iterates through them and move files out
    """
    dirs = os.listdir(src)

    # walk alpha folders
    for d in dirs:
        dirpath = os.path.join(src, d)

        # walk files in folder
        files = os.listdir(dirpath)
        for f in files:
            # move each out
            filepath = os.path.join(dirpath, f)
            copy_file(filepath, dst, test)

        # remove alpha folder
        #print('[.] removing folder %s' % (dirpath))
        # if not test:
        #    shutil.rmtree(dirpath)


def process(src, dst, unarchive, delarchives, movealpha, moveunalpha, skipbad, skipalt, delskipped, test):
    if test:
        print('****************************************************************')
        print('* TEST                                                         *')
        print('****************************************************************')

    print('[.] source folder: %s' % (src))
    print('[.] dest folder: %s' % (dst))
    os.makedirs(dst, exist_ok=True)

    if moveunalpha == True:
        do_moveunalpha(src, dst, test)
        return

    files = sorted(os.listdir(src))
    alphadirs = {}
    for f in files:
        srcf = os.path.join(src, f)
        if os.path.isdir(srcf):
            continue

        # calculate destination
        if movealpha:
            dstdir = get_dest_alpha_dir(srcf, dst, alphadirs)
        else:
            dstdir = dst

        # copy
        dstf = copy_file(srcf, dstdir, test)

        # skip bads/alt
        alt = False
        bad = False
        if skipbad:
            # skip bads
            bad = is_bad(dstf)
            if bad == True:
                skip(dstf, dst, delskipped, test)
                if delarchives and not unarchive and movealpha:
                    print('[.] deleting archive: %s' % (srcf))
                    del_file(srcf, test)

                dec_alphadir(dstf, alphadirs)
                continue

        if skipalt:
            # skip alts
            alt = is_alt(dstf)
            if alt == True:
                skip(dstf, dst, delskipped, test)
                if delarchives and not unarchive and movealpha:
                    print('[.] deleting archive: %s' % (srcf))
                    del_file(srcf, test)

                dec_alphadir(dstf, alphadirs)
                continue

        # finally unarchive
        if unarchive and (not alt and not bad):
            unar(dstf, dstdir, delarchives, test)

        if delarchives and not unarchive and movealpha:
            print('[.] deleting archive: %s' % (srcf))
            del_file(srcf, test)

    # done
    if movealpha == True:
        # ensure max 255 folders per root
        dirs = sorted(os.listdir(dst))
        n = 0
        nfolders = 1
        added = 0
        for d in dirs:
            dirpath = os.path.join(dst, d)
            if os.path.isfile(dirpath):
                continue

            n += 1
            if n > 255:
                # move
                mvpath = os.path.join(dst + '-' + str(nfolders), d)
                print('[.] destination path %s exceeds 255 folders, moving %s to %s' % (
                    dst, dirpath, mvpath))
                shutil.move(dirpath, mvpath)
                added += 1
                if added > 255:
                    nfolders += 1
                    added = 0


def main():
    d = "organize romsets."

    parser = argparse.ArgumentParser(
        description=d, formatter_class=RawTextHelpFormatter)

    parser.add_argument('--src', help='folder to operate on',
                        nargs=1, required=True)
    parser.add_argument('--dst', help='destination folder, same as --src if not specified.',
                        nargs=1, required=False)
    parser.add_argument('--flags', help='unarchive,delarchives,movealpha,moveunalpha,skipbad,skipalt,delskipped,test).',
                        nargs=1, required=True)
    args = parser.parse_args()

    unarchive = False
    delarchives = False
    movealpha = False
    moveunalpha = False
    skipbad = False
    skipalt = False
    delskipped = False
    test = False

    try:
        # get params
        params = args.flags[0].split(',')
        for p in params:
            if p == 'unarchive':
                unarchive = True
                unar = shutil.which('unar')
                if unar == None:
                    raise Exception(
                        '[x] ERROR: unar must be installed and in path!')

            if p == 'movealpha':
                movealpha = True
                if moveunalpha == True:
                    raise Exception(
                        '[x] ERROR: movealpha and moveunalpha cannot be specified together!')

            if p == 'moveunalpha':
                moveunalpha = True
                if movealpha == True or unarchive == True or skipbad == True or skipalt == True:
                    raise Exception(
                        '[x] ERROR: moveunalpha can only be specified alone!')

            if p == 'skipbad':
                skipbad = True
            if p == 'skipalt':
                skipalt = True
            if p == 'delskipped':
                delskipped = True
            if p == 'delarchives':
                delarchives = True
            if p == 'test':
                test = True

        if movealpha == False and moveunalpha == False and unarchive == False:
            raise Exception(
                '[x] ERROR: movealpha, moveunalpha and/or unarchive must be specified!')

        if (delskipped == True and skipbad == False and skipalt == False):
            print('[w] delskipped disabled since skipbad or skipalt not specified!')

        # do stuff
        dstdir = os.path.basename(args.src[0])
        process(args.src[0], os.path.join(args.dst[0], dstdir) if args.dst else args.src[0], unarchive, delarchives, movealpha, moveunalpha,
                skipbad, skipalt, delskipped, test)

        print('[.] Done!')

    except Exception as ex:
        # error
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
