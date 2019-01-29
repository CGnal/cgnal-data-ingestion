import os
from cgnal.utils.fs import create_dir_if_not_exists

test_path = os.path.dirname(os.path.abspath(__file__))

DATA_FOLDER = create_dir_if_not_exists(os.path.join(test_path, "..", "resources", "tests", "data"))
TMP_FOLDER = create_dir_if_not_exists(os.path.join(test_path, "..", "resources", "tests", "tmp"))
