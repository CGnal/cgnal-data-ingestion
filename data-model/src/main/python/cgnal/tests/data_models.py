import unittest
import os

from cgnal.tests import DATA_FOLDER

from cgnal.data.layer.pandas import PickleArchiver, CsvArchiver
from cgnal.data.layer.pandas.dao import DocumentDAO

TEST_DATA_PATH = DATA_FOLDER

class TestDocumentArchivers(unittest.TestCase):

    def test_pickle(self):
        dao = DocumentDAO()

        archiver = PickleArchiver(dao, os.path.join(DATA_FOLDER, 'test.pkl'))

        docs = list(archiver.retrieve())

        self.assertEquals(len(docs), 20)

    def test_csv(self):
        dao = DocumentDAO()

        archiver = CsvArchiver(dao, os.path.join(DATA_FOLDER, 'test.csv'))

        docs = list(archiver.retrieve())

        self.assertEquals(len(docs), 20)


    def test_retrieveById(self):
        dao = DocumentDAO()

        archiver = CsvArchiver(dao, os.path.join(DATA_FOLDER, 'test.csv'))

        _, doc = archiver.retrieve().next()

        _, doc2 = archiver.retrieveById(doc.uuid)

        self.assertEquals(doc.data, doc2.data)

    def test_update(self):
        dao = DocumentDAO()

        archiver = CsvArchiver(dao, os.path.join(DATA_FOLDER, 'test.csv'))

        _, doc = archiver.retrieve().next()

        doc.data.update({'symbols': ["enrico"]})

        archiver.archive(doc)

        _, doc2 = archiver.retrieveById(doc.uuid)

        self.assertEquals(doc2.data["symbols"], ["enrico"])


if __name__ == '__main__':
    unittest.main()
