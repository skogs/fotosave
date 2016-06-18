import sys
import os
import argparse
import errno
import hashlib
import shutil
from PIL import Image
from PIL.ExifTags import TAGS

def get_exif(fn):
    ret = {}
    i = Image.open(fn)
    info = i._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    return ret

def get_date(name):
    try:
        props = get_exif(name)
        return props['DateTime']
    except:
        return None

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d')
    parser.add_argument('src_dir', default='.')
    args = parser.parse_args()

    src = os.path.abspath(args.src_dir)
    dest_dir = os.path.abspath(args.d)

    if dest_dir.startswith(src):
        print('Destination directory needs to different than photos')
        exit()

    if os.path.isdir(src):
        for dir, _, files in os.walk(src):
            for file in files:
                dt = get_date(os.path.join(dir,file))
                if dt is not None:
                    print(file + ": " + dt)
                    exif_date,exif_time  = dt.split(' ')
                    (year,month,d) = exif_date.split(':')

                    src_photo_file = os.path.join(dir, file)
                    filename, file_extension = os.path.splitext(src_photo_file)

                    hasher = hashlib.sha1()
                    with open(src_photo_file, 'rb') as f:
                        hasher.update(f.read())
                    print(src_photo_file, hasher.hexdigest())

                    dest_photo_dir = os.path.join(dest_dir, year, month)
                    mkdir_p(dest_photo_dir)
                    dest_photo_file = os.path.join(dest_photo_dir, hasher.hexdigest()) \
                                       + file_extension

                    print "Copying " + src_photo_file + " to: " + dest_photo_file
                    shutil.copy(src_photo_file, dest_photo_file)
                else:
                    print(file)
    else:
        print(src + ": " + get_date(src))
