from cgnal.config import load as load_yaml

from logging import getLogger, basicConfig, config

from cgnal.logging import WithLoggingABC
from cgnal.logging import DEFAULT_LOG_LEVEL as LOG_LEVEL

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


def getDefaultLogger(level=levels[LOG_LEVEL]):
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
    configFile = load_yaml(path_to_file)
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
        ".yml": configFromYaml,
        ".yaml": configFromYaml,
        ".json": configFromJson
    }

    _, file_extension = os.path.splitext(path_to_file)

    if file_extension not in readers.keys():
        raise NotImplementedError(f"Reader for file extention {file_extension} is not supported")

    return readers[file_extension](path_to_file)


def logger(name=None):
    """
    Initialize default logger

    :param name: name to be used for the logger

    :return: default logger
    """
    return getLogger(name)
