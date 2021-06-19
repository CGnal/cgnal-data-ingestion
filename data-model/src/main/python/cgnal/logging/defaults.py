import os
import sys
from typing import Optional
from logging import getLogger, basicConfig, config, captureWarnings, Logger, FileHandler

from cgnal.config import load as load_yaml, merge_confs
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


def configFromJson(path_to_file: str):
    """
    Configure logger from json

    :param path_to_file: path to configuration file

    :return: configuration for logger
    """
    import json

    with open(path_to_file, 'rt') as f:
        configFile = json.load(f.read())
    config.dictConfig(configFile)


def configFromYaml(path_to_file: str):
    """
    Configure logger from yaml

    :param path_to_file: path to configuration file

    :return: configuration for logger
    """
    configFile = load_yaml(path_to_file)
    config.dictConfig(configFile)


def configFromFile(path_to_file: str):
    """
    Configure logger from file

    :param path_to_file: path to configuration file

    :return: configuration for logger
    """
    import os

    readers = {
        ".yml": configFromYaml,
        ".yaml": configFromYaml,
        ".json": configFromJson
    }

    _, file_extension = os.path.splitext(path_to_file)

    if file_extension not in readers.keys():
        raise NotImplementedError(f"Reader for file extention {file_extension} is not supported")

    return readers[file_extension](path_to_file)


def logger(name: Optional[str] = None) -> Logger:
    """
    Initialize named logger

    :param name: name to be used for the logger

    :return: default logger
    """
    return getLogger(name)


def setup_logger(name: str = "",
                 level: str = "INFO",
                 config_file: Optional[str] = None,
                 default_config_file: Optional[str] = None,
                 capture_warnings: bool = True) -> Logger:
    """
    Setup logger handling exceptions using error handler defined in configuration file.

    :param name: name of the logger to use. By default take the root logger
    :param level: logging level
    :param config_file: config file to use to setup logger
    :param default_config_file: default config_file to use
    :param capture_warnings: whether or not to capture warnings with logger

    :return: logger
    """
    captureWarnings(capture_warnings)

    if config_file is not None:
        import logging
        configuration = merge_confs(filenames=[config_file], default=default_config_file)
        for v in configuration.to_dict()['handlers'].values():
            if issubclass(eval(v['class']), FileHandler):
                create_dir_if_not_exists(os.path.dirname(v['filename']))
        config.dictConfig(configuration)

    basicConfig(level=level)
    logger = getLogger(name)

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.error(f"{exc_type.__name__}: {exc_value}", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception

    return logger
