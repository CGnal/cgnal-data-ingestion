import pandas as pd
from abc import abstractmethod
from collections import Iterable
from cgnal.data.model.core import IterGenerator
from cgnal.data.layer import DAO, Archiver
from cgnal.data.layer.hive.databases import Table


class HiveArchiver(Archiver):
    """ Base class for archivers that read and write from Hive """

    @abstractmethod
    def read(self, query):
        raise NotImplementedError

    @abstractmethod
    def write(self):
        raise NotImplementedError

    def __init__(self, dao):
        if not isinstance(dao, DAO):
            raise TypeError("Given DAO is not an instance of %s" % str(type(DAO)))
        self.dao = dao
        self.__data__ = None

    @property
    def data(self):
        return self.__data__

    @data.setter
    def data(self, value):
        self.set_data(value)

    def set_data(self, value):
        self.__data__ = value
        return self

    def retrieveById(self, idx):
        row = self.data.loc[idx]
        return self.dao.parse(row)

    def retrieve(self, condition=None):
        """
        Retrieve a tuple of rows from self.data

        :param condition: condition function used to filter self.data
        :return: tuple of filtered rows
        """
        rows = self.data if condition is None else condition(self.data)
        return (self.dao.parse(row) for _, row in rows.iterrows())

    def retrieveGenerator(self, condition=None):
        def __iterator__():
            return self.retrieve(condition=condition)
        return IterGenerator(__iterator__)

    def archiveOne(self, obj):
        return self.archiveMany([obj])

    def archiveMany(self, objs):
        def create_df(obj):
            s = self.dao.get(obj)
            s.name = self.dao.computeKey(obj)
            return s.to_frame().T

        new = pd.concat([create_df(obj) for obj in objs], sort=True)
        self.__data__ = pd.concat([self.__data__.loc[set(self.__data__.index).difference(new.index)], new], sort=True)
        return self

    def archive(self, objs):
        if isinstance(objs, Iterable):
            return self.archiveMany(objs)
        else:
            return self.archiveOne(objs)


class TableArchiver(HiveArchiver):

    def __init__(self, table, dao):
        super(TableArchiver, self).__init__(dao)

        assert isinstance(table, Table)
        self.table = table

    def write(self, partition_by=None, fields=None):
        self.table.write(df=self.data, partition_by=partition_by, fields=fields)

    def read(self, query, partitions=500):
        return self.table.to_df(query, partitions=partitions)


