from abc import ABCMeta, abstractproperty


DEFAULT_LOG_LEVEL = "INFO"


class WithLoggingABC(object):

    __metaclass__ = ABCMeta

    @abstractproperty
    def logger(self):
        """
        Logging class to be used to output logs within a class
        :return: None, outputs logs
        """
        pass
