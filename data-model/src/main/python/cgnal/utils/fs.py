import errno
import os

def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def create_dir_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

