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


def get_lexicographic_dirname(dirpath, first=False):
    id = 0 if first else -1
    dirName = sorted([os.path.join(dirpath, o).split("/")[-1] for o in os.listdir(dirpath) if os.path.isdir(os.path.join(dirpath, o))],
                       key=str.lower)[id]
    return dirName
