import os
import shutil
from tqdm import tqdm


def copyfileobj(fsrc, fdst, source_size, length=16*1024):
    with tqdm(total=source_size, unit='B', unit_scale=True) as pbar:
        while True:
            buf = fsrc.read(length)
            if not buf:
                break
            fdst.write(buf)
            pbar.update(len(buf))


def copy_file(src, dst):
    if shutil._samefile(src, dst):
        msg = "{!r} and {!r} are the same file".format(src, dst)
        raise shutil.SameFileError(msg)

    else:
        source_size = os.stat(src).st_size
        with open(src, 'rb') as fsrc:
            with open(dst, 'wb') as fdst:
                copyfileobj(fsrc, fdst, source_size)

    return dst


def get_file_ext(file_name):
    return os.path.splitext(file_name)[1]
