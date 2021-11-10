import os
import sys
from types import TracebackType
from importlib import import_module
from typing import Optional, List, Callable, Union, Any, Type
from logging import getLogger, basicConfig, config, captureWarnings, Logger, FileHandler
from deprecated import deprecated

from cgnal.typing import PathLike
from cgnal.config import load, merge_confs
from cgnal.logging import WithLoggingABC, DEFAULT_LOG_LEVEL, LevelsDict, LevelTypes, StrLevelTypes
from cgnal.utils.fs import create_dir_if_not_exists


levels: LevelsDict = {
    "CRITICAL": 50,
    "ERROR": 40,
    "WARNING": 30,
    "INFO": 20,
    "DEBUG": 10,
    "NOTSET": 0
}


class WithLogging(WithLoggingABC):

    @property
    def logger(self) -> Logger:
        """
        Create logger

        :return: default logger
        """
        nameLogger = str(self.__class__).replace("<class '", "").replace("'>", "")
        return getLogger(nameLogger)

    def logResult(self, msg: Union[Callable[..., str], str], level: StrLevelTypes = "INFO") -> Callable[..., Any]:
        def wrap(x: Any) -> Any:
            if isinstance(msg, str):
                self.logger.log(levels[level], msg)
            else:
                self.logger.log(levels[level], msg(x))
            return x
        return wrap


def getDefaultLogger(level: LevelTypes = levels[DEFAULT_LOG_LEVEL]) -> Logger:
    """
    Create default logger

    :param level: logging level

    :type level: str

    :return: logger
    """
    basicConfig(level=level)
    return getLogger()


@deprecated("This function is deprecated and will be removed in future versions. Use configFromFiles instead")
def configFromJson(path_to_file: PathLike) -> None:
    """
    Configure logger from json

    :param path_to_file: path to configuration file

    :return: configuration for logger
    """
    config.dictConfig(load(path_to_file))


@deprecated("This function is deprecated and will be removed in future versions. Use configFromFiles instead")
def configFromYaml(path_to_file: PathLike) -> None:
    """
    Configure logger from yaml

    :param path_to_file: path to configuration file

    :return: configuration for logger
    """
    config.dictConfig(load(path_to_file))


@deprecated("This function is deprecated and will be removed in future versions. Use configFromFiles instead")
def configFromFile(path_to_file: PathLike) -> None:
    """
    Configure logger from file

    :param path_to_file: path to configuration file

    :return: configuration for logger
    """
    config.dictConfig(load(path_to_file))


def configFromFiles(config_files: List[PathLike], capture_warnings: bool = True, catch_exceptions: Optional[str] = None) -> None:
    """
    Configure loggers from configuration obtained merging configuration files.
    If any handler inherits from FileHandler create the directory for its output files if it does not exist yet.

    :param config_files: list of configuration files
    :param capture_warnings: whether or not to capture warnings with logger
    :param catch_exceptions: name of the logger used to catch exceptions. If None do not catch exception with loggers.
    :return: None
    """

    captureWarnings(capture_warnings)

    configuration = merge_confs(filenames=config_files, default=None)
    for v in configuration.to_dict()['handlers'].values():
        splitted = v['class'].split('.')
        if issubclass(getattr(import_module('.'.join(splitted[:-1])), splitted[-1]), FileHandler):
            create_dir_if_not_exists(os.path.dirname(v['filename']))
    config.dictConfig(configuration)

    if catch_exceptions is not None:
        except_logger = getLogger(catch_exceptions)
        print(f'Catching excetptions with {except_logger.name} logger using handlers '
              f'{", ".join([x.name for x in except_logger.handlers])}')

        def handle_exception(exc_type: Type[BaseException], exc_value: BaseException, exc_traceback: TracebackType) -> None:
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
            else:
                except_logger.error(f"{exc_type.__name__}: {exc_value}", exc_info=(exc_type, exc_value, exc_traceback))

        sys.excepthook = handle_exception


def logger(name: Optional[str] = None) -> Logger:
    """
    Return a logger with the specified name, creating it if necessary.

    :param name: name to be used for the logger. If None return root logger

    :return: named logger
    """
    return getLogger(name)

