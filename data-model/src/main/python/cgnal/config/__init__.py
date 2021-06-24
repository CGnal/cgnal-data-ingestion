import os
import re
import sys
import cfg_load

from yaml import Loader, add_implicit_resolver, add_constructor, SequenceNode
from typing import List, Optional
from cfg_load import Configuration
from functools import reduce

__this_dir__, __this_filename__ = os.path.split(__file__)

path_matcher = re.compile(r'\$\{([^}^{]+)\}')


def path_constructor(loader: Loader, node: SequenceNode):
    """
    Extract the matched value, expand env variable, and replace the match
    """
    value = node.value
    match = path_matcher.match(value)
    env_var = match.group()[2:-1]
    return os.environ.get(env_var) + value[match.end():]


# define custom tag handler
def joinPath(loader: Loader, node: SequenceNode):
    seq = loader.construct_sequence(node)
    return os.path.join(*seq)


# register tag handlers
add_implicit_resolver('!path', path_matcher)
add_constructor('!path', path_constructor)
add_constructor('!joinPath', joinPath)


def load(filename):
    try:
        return cfg_load.load(filename, safe_load=False, Loader=Loader)
    except TypeError:
        return cfg_load.load(filename)


def get_all_configuration_file(application_file="application.yml", name_env="CONFIG_FILE"):
    confs = [os.path.join(path, application_file)
             for path in sys.path if os.path.exists(os.path.join(path, application_file))]
    env = [] if name_env not in os.environ.keys() else [os.environ[name_env]]
    print(f"Using Configuration files: {', '.join(confs + env)}")
    return confs + env


def merge_confs(filenames: List[str], default: Optional[str] = "defaults.yml"):
    lst = [default, *filenames] if default is not None else filenames
    print(f"Using Default Configuration file: {lst[0]}")
    return reduce(lambda config, fil: config.update(load(fil)), lst[1:], load(lst[0]))


class BaseConfig(object):
    def __init__(self, config):
        self.config = config

    def sublevel(self, name):
        return Configuration(self.config[name], self.config.meta, self.config.meta["load_remote"])

    def getValue(self, name):
        return self.config[name]

    def safeGetValue(self, name):
        return self.config.get(name, None)


class FileSystemConfig(BaseConfig):
    @property
    def root(self):
        return self.getValue("root")

    def getFolder(self, path):
        return self.config["folders"][path]

    def getFile(self, file):
        return self.config["files"][file]


class AuthConfig(BaseConfig):
    @property
    def method(self):
        return self.getValue("method")
    @property
    def filename(self):
        return self.getValue("filename")
    @property
    def user(self):
        return self.getValue("user")
    @property
    def password(self):
        return self.getValue("password")


class AuthService(BaseConfig):
    @property
    def url(self):
        return self.getValue("url")
    @property
    def check(self):
        return self.getValue("check")
    @property
    def decode(self):
        return self.getValue("decode")


class CheckService(BaseConfig):
    @property
    def url(self):
        return self.getValue("url")
    @property
    def login(self):
        return self.getValue("login")
    @property
    def logout(self):
        return self.getValue("logout")


class AuthenticationServiceConfig(BaseConfig):
    @property
    def secured(self):
        return self.getValue("secured")
    @property
    def ap_name(self):
        return self.getValue("ap_name")
    @property
    def jwt_free_endpoints(self):
        return self.getValue("jwt_free_endpoints")
    @property
    def auth_service(self):
        return AuthService(self.sublevel("auth_service"))
    @property
    def check_service(self):
        return CheckService(self.sublevel("check_service"))
    @property
    def cors(self):
        return self.getValue("cors")
