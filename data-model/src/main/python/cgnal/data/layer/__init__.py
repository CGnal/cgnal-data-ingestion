from abc import abstractmethod, ABCMeta

class Archiver(object):
    __metaclass__ = ABCMeta

    def dao(self):
        raise NotImplementedError

    @abstractmethod
    def retrieve(self, obj):
        raise NotImplementedError

    @abstractmethod
    def archive(self, obj):
        raise NotImplementedError


