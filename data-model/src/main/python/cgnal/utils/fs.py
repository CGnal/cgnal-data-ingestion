import errno
import os

from cgnal.typing import PathLike


def mkdir(path: PathLike) -> None:
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def create_dir_if_not_exists(directory: PathLike) -> PathLike:
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory


def get_lexicographic_dirname(dirpath: PathLike, first: bool = False) -> PathLike:
    return sorted([os.path.join(dirpath, o).split("/")[-1] for o in os.listdir(dirpath)
                   if os.path.isdir(os.path.join(dirpath, o))],
                  key=str.lower)[0 if first else -1]
