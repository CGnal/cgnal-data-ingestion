import os
import unittest
from logging import StreamHandler, FileHandler
from cgnal.logging.defaults import configFromFiles, logger
from cgnal.tests import DATA_FOLDER, TMP_FOLDER, clean_tmp_folder, unset_TMP_FOLDER
from cgnal.tests.core import TestCase, logTest

configFromFiles(config_files=[os.path.join(DATA_FOLDER, "logging.yml")], capture_warnings=True)


class TestSetupLogger(TestCase):
    root_logger = logger()
    cgnal_logger = logger(name="cgnal", level="INFO", catch_exceptions=True)

    @logTest
    def test_console_logger(self):
        self.root_logger.info("Example of logging with root logger!")
        self.assertEqual(self.root_logger.name, 'root')
        self.assertEqual(self.root_logger.level, 20)
        self.assertTrue(all([isinstance(h, StreamHandler) for h in self.root_logger.handlers]))

    @logTest
    def test_file_logger_name(self):
        self.assertEqual(self.cgnal_logger.name, 'cgnal')

    @logTest
    def test_file_logger_handlers(self):
        self.assertTrue(all([isinstance(h, FileHandler) for h in self.cgnal_logger.handlers]))

    @logTest
    def test_file_logger_path_creation(self):
        self.assertTrue(os.path.exists(TMP_FOLDER))
        self.assertTrue(all([os.path.exists(h.baseFilename) for h in self.cgnal_logger.handlers]))

    @logTest
    def test_file_logger_overwrite_level(self):
        self.assertEqual(self.cgnal_logger.level, 20)

    @logTest
    def test_file_logger_info_message(self):
        msg = "Example of logging with cgnal logger!"
        self.cgnal_logger.info(msg)
        with open(self.cgnal_logger.handlers[0].baseFilename, 'r') as fil:
            lin = fil.readline(-1)
        self.assertEqual(lin.split(" - ")[-1], f'{msg}\n')


if __name__ == '__main__':
    unittest.main()
    unset_TMP_FOLDER()
    clean_tmp_folder()
