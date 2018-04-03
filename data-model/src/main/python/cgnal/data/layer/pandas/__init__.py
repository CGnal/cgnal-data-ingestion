from abc import ABCMeta, abstractmethod, abstractproperty

from collections import Iterable

from cgnal.data.layer import Archiver
from cgnal.data.model.core import IterGenerator

class DataFrameDAO(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def computeKey(self, obj):
        raise NotImplementedError

    @abstractmethod
    def getRow(self, obj):
        raise NotImplementedError

    @abstractmethod
    def parseRow(self, row):
        raise NotImplementedError


import pandas as pd

class PandasArchiver(Archiver):

    def __init__(self, dao):
        if not isinstance(dao, DataFrameDAO):
            raise TypeError("Given DAO is not an instance of a CSV Dao")
        self.dao = dao

    @abstractproperty
    def data(self):
        raise NotImplementedError

    def retrieveById(self, uuid):
        row = self.data.loc[uuid]
        return self.dao.parseRow(row)

    def retrieve(self, condition = None):
        rows = self.data if condition is None else condition(self.data)
        return (self.dao.parseRow(row) for _, row in rows.iterrows())

    def retrieveGenerator(self, condition=None):
        def __iterator__():
            return self.retrieve(condition=condition)
        return IterGenerator( __iterator__ )

    def archiveOne(self, obj):
        return self.__insert__(obj)

    def __insert__(self, obj):
        self.data.loc[self.dao.computeKey( obj )] = self.dao.getRow(obj)

    def archiveMany(self, objs):
        return [self.__insert__(obj) for obj in objs]

    def archive(self, objs):
        if isinstance(objs, Iterable):
            return self.archiveMany(objs)
        else:
            return self.archiveOne(objs)

    def map(self, f, condition={}):
        for obj in self.retrieve(condition):
            yield f(obj)

    def foreach(self, f, condition={}):
        for obj in self.retrieve(condition):
            f(obj)


class CsvArchiver(PandasArchiver):

    def __init__(self, dao, filename, sep=";"):

        super(CsvArchiver, self).__init__(dao)

        if not isinstance(filename, str):
            raise TypeError("Collection %s is not a proper filename" % filename)

        self.filename = filename
        self.sep = sep

    __data__ = None

    @property
    def data(self):
        if self.__data__ is None:
            self.__data__ = pd.read_csv(self.filename, sep=self.sep)
        return self.__data__


class PickleArchiver(PandasArchiver):

    def __init__(self, dao, filename):

        super(PickleArchiver, self).__init__(dao)

        if not isinstance(filename, str):
            raise TypeError("Collection %s is not a proper filename" % filename)

        self.filename = filename

    __data__ = None

    @property
    def data(self):
        if self.__data__ is None:
            self.__data__ = pd.read_pickle(self.filename)
        return self.__data__





