import os
from cgnal.utils.fs import create_dir_if_not_exists

DATA_FOLDER = create_dir_if_not_exists(os.path.join(os.getcwd(), "cgnal", "resources", "tests", "data"))
TMP_FOLDER = create_dir_if_not_exists(os.path.join(os.getcwd(), "cgnal", "resources", "tests", "tmp"))