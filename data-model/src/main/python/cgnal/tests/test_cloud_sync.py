import unittest
import os
from time import sleep

from cgnal.tests import TMP_FOLDER
from cgnal.logging.defaults import getDefaultLogger
from cgnal.utils.cloud import CloudSync

logger = getDefaultLogger()

class TestDocumentArchivers(unittest.TestCase):

    url = "http://192.168.2.110:8686"

    test_file = "tests/test.txt"

    def test_base_function(self):
        sync = CloudSync(self.url, TMP_FOLDER)

        namefile = sync.get_if_not_exists(self.test_file)

        self.assertTrue(os.path.exists( namefile ))

        os.remove( namefile )


    def test_decorator(self):

        sync = CloudSync(self.url, TMP_FOLDER)

        @sync.get_if_not_exists_decorator
        def decorated_function(filename):
            return filename

        namefile = decorated_function(self.test_file)

        self.assertTrue(os.path.exists( namefile ))

        os.remove( namefile )

    def test_multiple(self):
        sync = CloudSync(self.url, TMP_FOLDER)

        namefile = sync.get_if_not_exists(self.test_file)

        self.assertTrue(os.path.exists(namefile))

        sleep(3)

        time = os.path.getmtime(namefile)

        namefile = sync.get_if_not_exists(self.test_file)

        time2 = os.path.getmtime(namefile)

        self.assertTrue(time==time2)

        os.remove(namefile)


    def test_upload(self):

        sync = CloudSync(self.url, TMP_FOLDER)

        namefile = sync.get_if_not_exists(self.test_file)

        upload = f"{self.test_file}.upload"

        os.rename(namefile, sync.pathTo(upload))

        sync.upload(upload)

        os.remove(sync.pathTo(upload))

        namefile_new = sync.get_if_not_exists(upload)

        self.assertTrue(os.path.exists(namefile_new))




if __name__ == "__main__":
    unittest.main()
