import unittest

import numpy as np
import pandas as pd

from cgnal.tests import TMP_FOLDER

from cgnal.logging.defaults import getDefaultLogger

from cgnal.data.layer.pandas import DataFrameDAO, SeriesDAO
from cgnal.data.layer.pandas.databases import Database
from cgnal.data.layer.pandas import TableArchiver

logger = getDefaultLogger()

class BaseArchiverTests(unittest.TestCase):

    ############################
    #### setup and teardown ####
    ############################

    tmp_folder = TMP_FOLDER

    @staticmethod
    def is_equal_dataframe_one_way(df1, df2):
        return all([df1[col].loc[row] == df2[col].loc[row]
                    for col in df1.columns for row, value in df1[col].items()])

    @staticmethod
    def is_equal_dataframe(df1, df2):
        return BaseArchiverTests.is_equal_dataframe_one_way(df1, df2) and \
               BaseArchiverTests.is_equal_dataframe_one_way(df2, df1)

    @staticmethod
    def is_equal_series(s1, s2):
        df1 = s1.to_frame("serie")
        df2 = s2.to_frame("serie")
        return BaseArchiverTests.is_equal_dataframe_one_way(df1, df2) and \
               BaseArchiverTests.is_equal_dataframe_one_way(df2, df1)


    def test_pickle_archiver_with_dataframes(self):

            db = Database(self.tmp_folder)

            table = db.table("my_table_df")

            df1 = pd.DataFrame({"a": np.ones(10), "b": 2 * np.ones(10)})
            df1.name = "row1"

            df2 = df1 * 2
            df2.name = "row2"

            dao = DataFrameDAO()

            a = TableArchiver(dao, table)

            a.archiveMany([df1, df2]).commit()

            _, df3 = a.retrieveById(df2.name)

            self.is_equal_dataframe(df2, df3)

            df3 = df3 * 2
            df3.name = "row2"

            a.archiveOne(df3).commit()

            b = TableArchiver(dao, table)

            df4 = df1 * 10
            df4.name = "row3"

            b.archiveMany([df1, df4]).commit()

            self.assertEqual(len(list(b.retrieve())), 3)


    def test_pickle_archiver_with_series(self):

            db = Database(self.tmp_folder)

            table = db.table("my_table_series")

            dao = SeriesDAO()

            s1 = pd.Series(np.ones(10), index=np.arange(0,20,2))

            a = TableArchiver(dao, table)

            a.archiveOne(s1).commit()

            b = TableArchiver(dao, table)

            s2 = [obj for _, obj in b.retrieve()][0]

            self.is_equal_series(s1, s2)




if __name__ == "__main__":
    unittest.main()
