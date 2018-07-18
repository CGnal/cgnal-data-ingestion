from abc import abstractmethod, ABCMeta

from cgnal.data.exceptions import NoTableException

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

    def map(self, f, condition={}):
        for index, obj in self.retrieve(condition):
            yield index, f(obj)

    def foreach(self, f, condition={}):
        for _, obj in self.retrieve(condition):
            f(obj)


class DAO(object):

    @abstractmethod
    def computeKey(self, obj):
        raise NotImplementedError

    @abstractmethod
    def get(self, obj):
        raise NotImplementedError

    @abstractmethod
    def parse(self, row):
        raise NotImplementedError


class DatabaseABC(object):
    """
    Abstract class for databases
    """

    @abstractmethod
    def table(self, table_name):
        pass


class TableABC(object):
    """
    Abstract class for tables
    """

    @abstractmethod
    def to_df(self, query):
        pass

    @abstractmethod
    def write(self, df, **kwargs):
        pass


class Writer(object):
    """
    Abstract class to write Tables
    """

    @property
    def table(self):
        raise NotImplementedError

    @abstractmethod
    def push(self, df):
        pass


class EmptyDatabase(DatabaseABC):
    """
    Class for empty Databases
    """

    def table(self, table_name):
        return NoTableException("No table found with name %s" % table_name)


