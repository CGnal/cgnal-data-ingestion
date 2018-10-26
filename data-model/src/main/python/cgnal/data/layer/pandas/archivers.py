from abc import abstractmethod

from collections import Iterable

import pandas as pd

from cgnal.data.layer import DAO
from cgnal.data.layer import Archiver
from cgnal.data.model.core import IterGenerator

from cgnal.data.layer.pandas.databases import Table

class PandasArchiver(Archiver):

    @abstractmethod
    def __read__(self):
        raise NotImplementedError

    @abstractmethod
    def __write__(self):
        raise NotImplementedError

    def __init__(self, dao):
        if not isinstance(dao, DAO):
            raise TypeError("Given DAO is not an instance of %s" % str(type(DAO)))
        self.dao = dao

        self.__data__ = None

    @property
    def data(self):
        if self.__data__ is None:
            return self.__read__()
        else:
            return self.__data__

    @data.setter
    def data(self, value):
        self.__data__ = value

    def commit(self):
        self.__write__()
        return self

    def retrieveById(self, uuid):
        row = self.data.loc[uuid]
        return self.dao.parse(row)

    def retrieve(self, condition = None):
        rows = self.data if condition is None else condition(self.data)
        return ( self.dao.parse(row) for _, row in rows.iterrows())

    def retrieveGenerator(self, condition=None):
        def __iterator__():
            return self.retrieve(condition=condition)
        return IterGenerator( __iterator__ )

    def archiveOne(self, obj):
        return self.archiveMany([obj])

    def archiveMany(self, objs):
        def create_df(obj):
            s = self.dao.get(obj)
            s.name = self.dao.computeKey(obj)
            return s.to_frame().T

        new = pd.concat( [create_df(obj) for obj in objs] )
        # print("here")
        # print(self.data.loc[set(self.data.index).difference(new.index)])
        # print(new)
        self.data = pd.concat( [self.data.loc[set(self.data.index).difference(new.index)], new] )
        return self

    def archive(self, objs):
        if isinstance(objs, Iterable):
            return self.archiveMany(objs)
        else:
            return self.archiveOne(objs)


class CsvArchiver(PandasArchiver):

    def __init__(self, filename, dao, sep=";"):

        super(CsvArchiver, self).__init__(dao)

        if not isinstance(filename, str):
            raise TypeError("Collection %s is not a proper filename" % filename)

        self.filename = filename
        self.sep = sep

    def __write__(self):
        self.data.to_csv(self.filename, sep=self.sep)

    def __read__(self):
        return pd.read_csv(self.filename, sep=self.sep)


class PickleArchiver(PandasArchiver):

    def __init__(self, filename, dao):

        super(PickleArchiver, self).__init__(dao)

        if not isinstance(filename, str):
            raise TypeError("Collection %s is not a proper filename" % filename)

        self.filename = filename

    def __write__(self):
        self.data.to_pickle(self.filename)

    def __read__(self):
        return pd.read_pickle(self.filename)


class TableArchiver(PandasArchiver):

    def __init__(self, table, dao):
        super(TableArchiver, self).__init__(dao)

        assert isinstance(table, Table)
        self.table = table

    def __write__(self):
        self.table.write( self.data, overwrite=True )

    def __read__(self):
        try:
            return self.table.data
        except (IOError):
            return pd.DataFrame()