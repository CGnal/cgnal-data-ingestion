from logging import getLogger, basicConfig, config

from . import WithLoggingABC
from . import DEFAULT_LOG_LEVEL as LOG_LEVEL

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

def getDefaultLogger(level = levels[LOG_LEVEL]):
    """
    Create default logger

    :param level: logging level

    :type level: str

    :return: logger
    """
    basicConfig(level=level)
    return getLogger()


def configFromJson(path_to_file):
    """
    Configure logger from json

    :param path_to_file: path to configuration file

    :type path_to_file: str

    :return: configuration for logger
    """
    import json

    with open(path_to_file, 'rt') as f:
        configFile = json.load(f.read())
    config.dictConfig(configFile)


def configFromYaml(path_to_file):
    """
    Configure logger from yaml

    :param path_to_file: path to configuration file

    :type path_to_file: str

    :return: configuration for logger
    """
    import yaml

    with open(path_to_file, 'rt') as f:
        configFile = yaml.safe_load(f.read())
    config.dictConfig(configFile)


def configFromFile(path_to_file):
    """
    Configure logger from file

    :param path_to_file: path to configuration file

    :type path_to_file: str

    :return: configuration for logger
    """
    import os

    readers = {
        ".yaml": configFromYaml,
        ".json": configFromJson
    }

    _, file_extension = os.path.splitext(path_to_file)

    return readers[file_extension](path_to_file)


def logger(name=None):
    """
    Initialize default logger

    :param name: name to be used for the logger

    :return: default logger
    """
    return getLogger(name)