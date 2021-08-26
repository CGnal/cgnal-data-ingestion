from datetime import datetime as dt
from deprecated import deprecated

from cgnal.logging import DEFAULT_LOG_LEVEL, StrLevelTypes

levels = {"ERROR": 0, "WARNING": 1, "INFO": 2, "DEBUG": 3}


@deprecated("This class is deprecated and will be removed in future releases. Use logging.Logger instead.")
class Logger(object):
    """
    A class to report different levels of log messages
    """
    def __init__(self, log_level: StrLevelTypes) -> None:
        self.log_level = log_level

    def __printer__(self, msg: str, level: StrLevelTypes) -> None:
        """
        Print log

        :param msg: the output message to report
        :param level: the level of the message
        :return:the message
        """
        if levels[self.log_level] >= levels[level]:
            print("%s - %s: %s" % (str(dt.utcnow()), level, msg) )

    def info(self, msg: str) -> None:
        """
        Print info message
        :param msg: the output message to report
        """
        self.__printer__(msg, "INFO")

    def debug(self, msg: str) -> None:
        """
        Print debug message

        :param msg: the output message to report
        """
        self.__printer__(msg, "DEBUG")

    def warn(self, msg: str) -> None:
        """
        Print warning message

        :param msg: the output message to report
        """
        self.__printer__(msg, "WARNING")

    def warning(self, msg: str) -> None:
        """
        Print warning message

        :param msg: the output message to report
        """
        self.__printer__(msg, "WARNING")

    def error(self, msg: str) -> None:
        """
        Print error message

        :param msg: the output message to report
        """
        self.__printer__(msg, "ERROR")


_logger = Logger(DEFAULT_LOG_LEVEL)


@deprecated("This class is deprecated and will be removed in future releases. "
            "Use cgnal.logging.defaults.logger instead.")
def logger() -> Logger:
    """
    Initialize default logger

    :return: default logger
    """
    return _logger
