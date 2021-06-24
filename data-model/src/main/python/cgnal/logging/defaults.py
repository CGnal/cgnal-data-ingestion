import os
import sys
from importlib import import_module
from typing import Optional, List
from logging import getLogger, basicConfig, config, captureWarnings, Logger, FileHandler
from deprecated import deprecated

from cgnal.config import load, merge_confs
from cgnal.logging import WithLoggingABC, DEFAULT_LOG_LEVEL as LOG_LEVEL
from cgnal.utils.fs import create_dir_if_not_exists

levels = {
    "CRITICAL"	: 50 ,
    "ERROR"	    : 40 ,
    "WARNING"	: 30 ,
    "INFO"	    : 20 ,
    "DEBUG"	    : 10 ,
    "NOTSET"	: 0
}


class WithLogging(WithLoggingABC):

    @property
    def logger(self):
        """
        Create logger

        :return: default logger
        """
        nameLogger = str(self.__class__).replace("<class '", "").replace("'>", "")
        return getLogger(nameLogger)

    def logResult(self, msg, level="INFO"):
        def wrap(x):
            if isinstance(msg, str):
                self.logger.log(levels[level], msg)
            else:
                self.logger.log(levels[level], msg(x))
            return x
        return wrap


def getDefaultLogger(level: str = levels[LOG_LEVEL]) -> Logger:
    """
    Create default logger

    :param level: logging level

    :type level: str

    :return: logger
    """
    basicConfig(level=level)
    return getLogger()


@deprecated("This function is deprecated and will be removed in future versions. Use configFromFiles instead")
def configFromJson(path_to_file: str) -> None:
    """
    Configure logger from json

    :param path_to_file: path to configuration file

    :return: configuration for logger
    """
    config.dictConfig(load(path_to_file))


@deprecated("This function is deprecated and will be removed in future versions. Use configFromFiles instead")
def configFromYaml(path_to_file: str) -> None:
    """
    Configure logger from yaml

    :param path_to_file: path to configuration file

    :return: configuration for logger
    """
    config.dictConfig(load(path_to_file))


@deprecated("This function is deprecated and will be removed in future versions. Use configFromFiles instead")
def configFromFile(path_to_file: str) -> None:
    """
    Configure logger from file

    :param path_to_file: path to configuration file

    :return: configuration for logger
    """
    config.dictConfig(load(path_to_file))


def __handle_exception__(exc_type, exc_value, exc_traceback, logger) -> None:
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error(f"{exc_type.__name__}: {exc_value}", exc_info=(exc_type, exc_value, exc_traceback))


def configFromFiles(config_files: List[str], capture_warnings: bool = True, catch_exceptions: Optional[str] = None):
    """
    Configure loggers from configuration obtained merging configuration files.
    If any handler inherits from FileHandler create the directory for its output files if it does not exist yet.

    :param config_files: list of configuration files
    :param capture_warnings: whether or not to capture warnings with logger
    :param catch_exceptions: name of the logger used to catch exceptions. If None do not catch exception with loggers.
    :return: None
    """

    captureWarnings(capture_warnings)

    configuration = merge_confs(filenames=config_files, default=None)
    for v in configuration.to_dict()['handlers'].values():
        splitted = v['class'].split('.')
        if issubclass(getattr(import_module('.'.join(splitted[:-1])), splitted[-1]), FileHandler):
            create_dir_if_not_exists(os.path.dirname(v['filename']))
    config.dictConfig(configuration)

    if catch_exceptions is not None:
        sys.excepthook = lambda exctype, value, traceback: __handle_exception__(exctype, value, traceback,
                                                                                logger=getLogger(catch_exceptions))


def logger(name: Optional[str] = None) -> Logger:
    """
    Return a logger with the specified name, creating it if necessary.

    :param name: name to be used for the logger. If None return root logger

    :return: named logger
    """
    return getLogger(name)

