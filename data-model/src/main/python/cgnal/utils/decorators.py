import os
from glob import glob

from functools import wraps

import pandas as pd
from cgnal.utils.fs import create_dir_if_not_exists

def cache(func):
    """
    Decorator to cache function return values

    :param func: input function
    :return: function wrapper
    """
    @wraps(func)
    def _wrap(obj):
        try:
            return obj.__cache__[func.func_name]
        except KeyError:
            score = func(obj)
            obj.__cache__[func.func_name] = score
            return score
    return _wrap


class Cached(object):

    def clear_cache(self):
        """
        Clear cache of the object

        :return: None
        """
        self.__cache__ = {}

    def save_pickles(self, path):
        """
        Save pickle in given path

        :param path: saving path
        :return: None
        """
        path = create_dir_if_not_exists(path)

        for k, _ in self.__cache__.items():
            data = getattr(self, k)
            Cached.save_element( os.path.join(path, k), data )

    @staticmethod
    def save_element(filename, obj):
        """
        Save given object in given file

        :param filename: saving path
        :param obj: object to be saved
        :return: None
        """
        if isinstance(obj, dict):
            create_dir_if_not_exists(filename)
            [Cached.save_element( os.path.join(filename, k), v ) for k, v in obj.items()]
        elif isinstance(obj, pd.DataFrame) or isinstance(obj, pd.Series):
            pd.to_pickle(obj, "%s.p" % filename)
        else:
            raise ValueError("Cannot save input of type %s" % str(obj.__class__))

    @staticmethod
    def load_element(filename):
        """
        Load pickle at given path (or all pickles in given folder)

        :param path: path to pickles
        :return: content of the read pickle
        """
        if os.path.isdir(filename):
            return {Cached.__reformat_name(path): Cached.load_element(os.path.splitext(path)[0])
                    for path in glob(os.path.join(filename, "*"))}
        else:
            return pd.read_pickle(filename + ".p")

    @staticmethod
    def __reformat_name(filename):
        """
        Reformat file name to make it readable with load_element

        :param filename: file name to reformat
        :return: reformatted filename
        """
        if os.path.isfile(filename):
            return os.path.basename(filename).replace(".p", "")
        else:
            return os.path.basename(filename)



