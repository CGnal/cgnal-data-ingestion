import pandas as pd  # type: ignore
from abc import abstractmethod, ABC
from bson.objectid import ObjectId  # type: ignore
from typing import Any, Callable, Optional, Iterator, TypeVar, Union, Hashable, Dict

from cgnal import T
from cgnal.data.model.text import Document
from cgnal.data.model.core import IterGenerator
from cgnal.data.exceptions import NoTableException


DataVal = TypeVar('DataVal', Document, pd.DataFrame, pd.Series)


class DAO(ABC):
    """ Data Access Object"""

    @abstractmethod
    def computeKey(self, obj: DataVal) -> Union[Hashable, Dict[str, ObjectId]]: ...

    @abstractmethod
    def get(self, obj: DataVal) -> Union[pd.Series, dict]: ...

    @abstractmethod
    def parse(self, row: Any) -> Union[Document, pd.DataFrame, pd.Series]: ...


class Archiver(ABC):
    """ Object that retrieve data from source and stores it in memory """

    def dao(self) -> DAO: ...

    @abstractmethod
    def retrieve(self, *args: Any, **kwargs: Any) -> Iterator[Union[pd.Series, pd.DataFrame, Document]]: ...

    @abstractmethod
    def archive(self, obj: DataVal) -> 'Archiver': ...

    def map(self, f: Callable[[DataVal], T], *args: Any, **kwargs: Any) -> Iterator[T]:
        for obj in self.retrieve(*args, **kwargs):  # type: DataVal
            yield f(obj)

    def foreach(self, f: Callable[[DataVal], T], *args, **kwargs) -> None:
        for obj in self.retrieve(*args, **kwargs):  # type: DataVal
            f(obj)

    def retrieveGenerator(self, *args: Any, **kwargs: Any) -> IterGenerator[DataVal]:
        def __iterator__():
            return self.retrieve(*args, **kwargs)
        return IterGenerator(__iterator__)


class TableABC(ABC):
    """
    Abstract class for tables
    """

    @abstractmethod
    def to_df(self, query: str) -> pd.DataFrame: ...

    @abstractmethod
    def write(self, df: pd.DataFrame, **kwargs: Any) -> None: ...


class DatabaseABC(ABC):
    """
    Abstract class for databases
    """

    @abstractmethod
    def table(self, table_name: str) -> Optional[TableABC]: ...


class Writer(ABC):
    """
    Abstract class to write Tables
    """

    @property
    @abstractmethod
    def table(self) -> TableABC: ...

    @abstractmethod
    def push(self, df: pd.DataFrame) -> None: ...


class EmptyDatabase(DatabaseABC):
    """
    Class for empty Databases
    """

    def table(self, table_name: str) -> None:
        raise NoTableException(f"No table found with name {table_name}")


