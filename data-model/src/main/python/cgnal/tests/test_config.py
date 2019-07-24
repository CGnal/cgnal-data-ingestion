import unittest
import os

from cgnal.logging import LoggingConfig
from cgnal.logging.defaults import getDefaultLogger, configFromFile
from cgnal.tests import DATA_FOLDER
from cgnal.config import get_all_configuration_file, __this_dir__ as config_dir, merge_confs, \
    BaseConfig, FileSystemConfig


TEST_DATA_PATH = DATA_FOLDER
logger = getDefaultLogger()

class TestConfig(BaseConfig):

    @property
    def logging(self):
        return LoggingConfig(self.sublevel("logging"))

    @property
    def fs(self):
        return FileSystemConfig(self.sublevel("fs"))


class TestDocumentArchivers(unittest.TestCase):


    def test_config(self):
        test_file = "defaults.yml"

        os.environ["CONFIG_FILE"] = os.path.join(TEST_DATA_PATH, test_file)

        config = TestConfig(BaseConfig(merge_confs(
            get_all_configuration_file(),
            os.path.join(config_dir, "defaults.yml")
        )).sublevel("test"))

        logger.info(f"Logging: {config.logging.level}")
        self.assertEqual(config.logging.level, "DEBUG")

        logger.info(f"Get File: {config.fs.getFile('credentials')}")
        self.assertEqual(config.fs.getFile("credentials"), os.path.join("/this/is/a/folder","myfolder","credentials.p"))

    def test_read_logging_config(self):
        config_file = "logging.yml"

        configFromFile(os.path.join(TEST_DATA_PATH, config_file))

        logger.info("Example of logging!")




if __name__ == "__main__":
    unittest.main()
