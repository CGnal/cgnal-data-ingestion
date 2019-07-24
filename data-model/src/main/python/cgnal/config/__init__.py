import os

import yaml
import cfg_load
from cfg_load import Configuration

import sys
from functools import reduce

__this_dir__, __this_filename__ = os.path.split(__file__)

## define custom tag handler
def joinPath(loader, node):
    seq = loader.construct_sequence(node)
    return os.path.join(*seq)

## register the tag handler
yaml.add_constructor('!joinPath', joinPath)

def load(filename):
    return cfg_load.load(filename, safe_load=False, Loader=yaml.Loader)

def get_all_configuration_file(application_file="application.yml"):
    confs = [os.path.join(path, application_file)
            for path in sys.path if os.path.exists(os.path.join(path, application_file))]
    env = [] if "CONFIG_FILE" not in os.environ.keys() else [os.environ["CONFIG_FILE"]]
    print(f"Using Configuration files: {', '.join(confs + env)}")
    return confs + env


def merge_confs(filenames, default="defaults.yml"):
    print(f"Using Default Configuration file: {default}")
    return reduce(lambda agg, filename: agg.update( load(filename) ), filenames, load(default))


class BaseConfig(object):
    def __init__(self, config):
        self.config = config

    def sublevel(self, name):
        return Configuration(self.config[name], self.config.meta, self.config.meta["load_remote"])

    def getValue(self, name):
        return self.config[name]


class FileSystemConfig(BaseConfig):
    @property
    def root(self):
        return self.getValue("root")

    def getFolder(self, path):
        return self.config["folders"][path]

    def getFile(self, file):
        return self.config["files"][file]


