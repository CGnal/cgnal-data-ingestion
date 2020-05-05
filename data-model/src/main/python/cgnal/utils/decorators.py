import os
import inspect
import pandas as pd
from glob import glob
from functools import wraps, partial

from cgnal.utils.dict import union
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
            return obj.__dict__[func.__name__]
        except KeyError:
            score = func(obj)
            obj.__dict__[func.__name__] = score
            return score
    _wrap.__name__ = func.__name__
    return _wrap


def lazyproperty(obj):
    return property(cache(obj))


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


def paramCheck(function, allow_none=True):

    @wraps(function)
    def check(*arguments, **kwargs):

        default_values = inspect.getfullargspec(function).defaults
        annotations = inspect.getfullargspec(function).annotations
        _args = inspect.getfullargspec(function).args[:-len(default_values)] if default_values \
            else inspect.getfullargspec(function).args

        non_default_args = [arg for arg in _args if (arg in annotations.keys() and arg != 'self')]
        default_args = inspect.getfullargspec(function).args[-len(default_values):] if default_values else []

        arg_dict = union({argument: {'type': annotations[argument], 'value': None} for argument in non_default_args},
                         {argument: {'type': annotations.get(argument) if annotations.get(argument) \
                             else type(default_values[index]), 'value': default_values[index]}
                          for index, argument in enumerate(default_args)}
                         )
        for index, arg in enumerate(inspect.getfullargspec(function).args):

            if arg != 'self':
                argIn = arguments[index] if index < len(arguments) else kwargs.get(arg, arg_dict[arg]['value'])
                if argIn is None:
                    if allow_none is False: raise ValueError(f"{arg} cannot be None")
                else:
                    if (not isinstance(argIn, arg_dict[arg]['type'])) and (arg_dict[arg]['type'].__name__ != 'NoneType'):
                        raise TypeError(f"{arg} parameter must be of type {arg_dict[arg]['type'].__name__}")

        return function(*arguments, **kwargs)
    return check


param_check = lambda with_none: partial(paramCheck, allow_none=with_none)

