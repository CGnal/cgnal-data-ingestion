import os
from mongomock import MongoClient
from cgnal.utils.fs import create_dir_if_not_exists

test_path = os.path.dirname(os.path.abspath(__file__))

DATA_FOLDER = create_dir_if_not_exists(os.path.join(test_path, "..", "resources", "tests", "data"))
TMP_FOLDER = create_dir_if_not_exists(os.path.join(test_path, "..", "resources", "tests", "tmp"))
os.environ['TMP_LOG_FOLDER'] = os.path.join(TMP_FOLDER, 'logs')

DB_NAME = "db"

client = MongoClient()

db = client[DB_NAME]


def clean_tmp_folder():
    os.system(f'rm -rf {TMP_FOLDER}/*')


def unset_TMP_FOLDER():
    del os.environ["TMP_LOG_FOLDER"]
