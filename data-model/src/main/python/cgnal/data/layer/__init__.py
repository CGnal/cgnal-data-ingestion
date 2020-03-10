from abc import abstractmethod, ABCMeta

from cgnal.data.model.core import IterGenerator
from cgnal.data.exceptions import NoTableException


class Archiver(object):
    """ Object that retrieve data from source and stores it in memory """

    __metaclass__ = ABCMeta

    def dao(self):
        raise NotImplementedError

    @abstractmethod
    def retrieve(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def archive(self, obj):
        raise NotImplementedError

    def map(self, f, *args, **kwargs):
        for obj in self.retrieve(*args, **kwargs):
            yield f(obj)

    def foreach(self, f, *args, **kwargs):
        for obj in self.retrieve(*args, **kwargs):
            f(obj)

    def retrieveGenerator(self, *args, **kwargs):
        def __iterator__():
            return self.retrieve(*args, **kwargs)
        return IterGenerator( __iterator__ )



class DAO(object):
    """ Data Access Object"""

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


