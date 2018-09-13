from datetime import datetime as dt
from . import DEFAULT_LOG_LEVEL as LOG_LEVEL

levels = {"ERROR": 0, "WARN": 1, "INFO": 2, "DEBUG": 3}


class Logger(object):
    """
    A class to report different levels of log messages
    """
    def __init__(self, log_level):
        self.log_level = log_level

    def __printer__(self, msg, level):
        """
        :param msg: the output message to report
        :param level: the level of the message
        :type msg: str
        :type level: str
        :return:the message
        """
        if levels[self.log_level] >= levels[level]:
            print("%s - %s: %s" % (str(dt.utcnow()), level, msg) )

    def info(self, msg):
        """
        :param msg: the output message to report
        :type msg: str
        """
        self.__printer__(msg, "INFO")

    def debug(self, msg):
        """
        :param msg: the output message to report
        :type msg: str
        """
        self.__printer__(msg, "DEBUG")

    def warn(self, msg):
        """
        :param msg: the output message to report
        :type msg: str
        """
        self.__printer__(msg, "WARN")

    def error(self, msg):
        """
        :param msg: the output message to report
        :type msg: str
        """
        self.__printer__(msg, "ERROR")


_logger = Logger(LOG_LEVEL)


def logger():
    """
    Initialize default logger

    :return: default logger
    """
    return _logger
