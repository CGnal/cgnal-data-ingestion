import unittest
import os

import pandas as pd

from cgnal.utils.fs import mkdir
from cgnal.data.layer.pandas import DataFrameDAO, PickleArchiver, CsvArchiver
from cgnal.data.model.text   import Document

__this_dir__, __this_filename__ = os.path.split(__file__)

TEST_DATA_PATH = __this_dir__

class DocumentDAO(DataFrameDAO):
    def computeKey(self, doc):
        return doc.uuid

    def getRow(self, doc):
        return pd.Series(doc.data, name=self.computeKey(doc))

    def parseRow(self, row):
        return Document(row.name, row.to_dict())

class TestDocumentArchivers(unittest.TestCase):

    def test_pickle(self):
        dao = DocumentDAO()

        archiver = PickleArchiver(dao, './test.pkl')

        docs = list(archiver.retrieve())

        self.assertEquals(len(docs), 20)

    def test_csv(self):
        dao = DocumentDAO()

        archiver = CsvArchiver(dao, './test.csv')

        docs = list(archiver.retrieve())

        self.assertEquals(len(docs), 20)


    def test_retrieveById(self):
        dao = DocumentDAO()

        archiver = CsvArchiver(dao, './test.csv')

        doc = archiver.retrieve().next()

        doc2 = archiver.retrieveById(doc.uuid)

        self.assertEquals(doc.data, doc2.data)

    def test_update(self):
        dao = DocumentDAO()

        archiver = CsvArchiver(dao, './test.csv')

        doc = archiver.retrieve().next()

        doc.data.update({'symbols': ["enrico"]})

        archiver.archive(doc)

        doc2 = archiver.retrieveById(doc.uuid)

        self.assertEquals(doc2.data["symbols"], ["enrico"])


if __name__ == '__main__':
    unittest.main()

