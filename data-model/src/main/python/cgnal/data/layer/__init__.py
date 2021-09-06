import pandas as pd  # type: ignore
from abc import abstractmethod, ABC
from typing import Any, Callable, Optional, Iterator, TypeVar
from cgnal import T
from cgnal.data.model.text import Document
from cgnal.data.model.core import IterGenerator
from cgnal.data.exceptions import NoTableException


DataVal = TypeVar('DataVal', Document, pd.DataFrame, pd.Series)


class DAO(ABC):
    """ Data Access Object"""

    @abstractmethod
    def computeKey(self, obj): ...

    @abstractmethod
    def get(self, obj): ...

    @abstractmethod
    def parse(self, row: Any) -> Any: ...


class Archiver(ABC):
    """ Object that retrieve data from source and stores it in memory """

    # TODO: why is this a method and not an (abstract, settable) property? In PandasArchiver it is used as such...
    def dao(self) -> DAO: ...

    @abstractmethod
    def retrieve(self, *args: Any, **kwargs: Any) -> Iterator[DataVal]: ...

    @abstractmethod
    def archive(self, obj: DataVal) -> 'Archiver': ...

    def map(self, f: Callable[[DataVal], T], *args: Any, **kwargs: Any) -> Iterator[T]:
        for obj in self.retrieve(*args, **kwargs):  # type: DataVal
            yield f(obj)

    # TODO: this method does not return anything: what is its point?
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


