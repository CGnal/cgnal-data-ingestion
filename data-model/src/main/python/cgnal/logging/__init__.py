from abc import ABCMeta, abstractmethod
from cgnal.config import BaseConfig

DEFAULT_LOG_LEVEL = "INFO"


class WithLoggingABC(object):

    __metaclass__ = ABCMeta

    @property
    @abstractmethod
    def logger(self):
        """
        Logging class to be used to output logs within a class
        :return: None, outputs logs
        """
        pass


class LoggingConfig(BaseConfig):
    @property
    def level(self):
        return self.getValue("level")

    @property
    def filename(self):
        return self.getValue("filename")
