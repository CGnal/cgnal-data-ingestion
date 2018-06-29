import os
import pickle
import pandas as pd
from glob import glob
from os.path import basename

from cgnal.utils.fs import create_dir_if_not_exists
from cgnal.data.layer import DatabaseABC, TableABC
from cgnal.logging.defaults import WithLogging

class Database(WithLogging, DatabaseABC):

    def __init__(self, name, extension="p"):
        """
        Class implementing standard read and write methods to pickle data sources

        :param name: path to pickles
        :param extension: standard pickle extension

        :type name: str
        :type extension: str
        """
        if not os.path.exists(name):
            self.logger.info("Creating new database %s" % name)
        self.name = create_dir_if_not_exists( name )
        self.extenstion = extension

    @property
    def tables(self):
        """
        Complete pickle names with appropriate extension

        :return: pickle names with appropriate extensions
        """
        return map(lambda x: basename(x)[:-len(self.extenstion)],
                   glob(os.path.join(self.name, "*%s" % self.extenstion)))

    def table(self, table_name):
        """
        Table selector

        :param table_name: name of the table

        :type table_name: str

        :return: object of class PickleTable
        """
        if table_name in self.tables:
            return Table(self, table_name)
        else:
            self.logger.warn("Table %s not found in database %s" % (table_name, self.name))
            return Table(self, table_name)


class Table(WithLogging, TableABC):

    def __init__(self, db, table_name):
        """
        Class implementing a constructor to interface with gtaa from pickle databases

        :param db: object of class PickleDatabase
        :param table_name: name of the table

        :type db: Database
        :type table_name: str
        """

        if not isinstance(db, Database):
            raise ValueError("The db should be of type %s" % type(Database))

        self.db = db
        self.name = table_name

    @property
    def filename(self):
        """
        Path to pickle

        :return: path to pickle file
        """
        return os.path.join(self.db.name, '%s.p' % self.name)

    @property
    def data(self):
        """
        Read pickle

        :return: pd.DataFrame or pd.Series read from pickle
        """
        return pd.read_pickle(self.filename)

    def write(self, df, overwrite=False):
        """
        Write pickle of data, eventually outer joined with an input DataFrame

        :param df: input data

        :type df: pd.DataFrame

        :return: None
        """

        # self.data can fail with:
        #   - KeyError if it tries to read a non-pickle file
        #   - IOError if the file does not exist
        try:
            _in = self.data if not overwrite else None
        except (KeyError, IOError):
            _in = None

        # pd.concat can fail with a TypeError if df is not an NDFrame object
        try:
            _df = pd.concat([_in, df])
        except TypeError:
            _df = df

        _df.to_pickle(self.filename)
