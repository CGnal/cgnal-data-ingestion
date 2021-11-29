import pandas as pd  # type: ignore
from pandas.errors import EmptyDataError  # type: ignore
from abc import abstractmethod, ABC
from collections import Iterable
from typing import Optional, Union, Iterator, Callable, List, Iterable as IterableType
from cgnal.typing import PathLike
from cgnal.data.model.core import IterGenerator
from cgnal.data.layer import DAO, Archiver, DataVal
from cgnal.data.layer.pandas.dao import DataFrameDAO, SeriesDAO, DocumentDAO
from cgnal.data.layer.pandas.databases import Table


Daos = Union[DataFrameDAO, SeriesDAO, DocumentDAO]


class PandasArchiver(Archiver, ABC):

    @abstractmethod
    def __read__(self) -> pd.DataFrame: ...

    @abstractmethod
    def __write__(self) -> None: ...

    def __init__(self, dao: Daos) -> None:
        if not isinstance(dao, DAO):
            raise TypeError(f"Given dao is not an instance of {'.'.join([DAO.__module__, DAO.__name__])}")
        self.dao = dao
        self.__data__: Optional[pd.DataFrame] = None

    @property
    def data(self) -> pd.DataFrame:
        if self.__data__ is None:
            self.data = self.__read__()
        return self.__data__

    @data.setter
    def data(self, value: pd.DataFrame) -> None:
        self.__data__ = value

    def commit(self) -> 'PandasArchiver':
        self.__write__()
        return self

    def retrieveById(self, uuid: pd.Index) -> DataVal:
        row = self.data.loc[uuid]
        return self.dao.parse(row)

    def retrieve(self, condition: Optional[Callable[[pd.DataFrame], pd.DataFrame]] = None,
                 sort_by: Optional[Union[str, List[str]]] = None) -> Iterator[DataVal]:
        rows = self.data if condition is None else condition(self.data)
        rows = rows.sort_values(sort_by) if sort_by is not None else rows
        return (self.dao.parse(row) for _, row in rows.iterrows())

    def retrieveGenerator(self, condition: Optional[Callable[[pd.DataFrame], pd.DataFrame]] = None,
                          sort_by: Optional[Union[str, List[str]]] = None) -> IterGenerator[DataVal]:
        def __iterator__():
            return self.retrieve(condition=condition, sort_by=sort_by)
        return IterGenerator(__iterator__)

    def archiveOne(self, obj: DataVal):
        return self.archiveMany([obj])

    def archiveMany(self, objs: IterableType[DataVal]) -> 'PandasArchiver':
        def create_df(obj):
            s = self.dao.get(obj)
            s.name = self.dao.computeKey(obj)
            return s.to_frame().T

        new = pd.concat([create_df(obj) for obj in objs], sort=True)
        self.data = pd.concat([self.data.loc[set(self.data.index).difference(new.index)], new], sort=True)
        return self

    def archive(self, objs: Union[IterableType[DataVal], DataVal]):
        if isinstance(objs, Iterable):
            return self.archiveMany(objs)
        else:
            return self.archiveOne(objs)


class CsvArchiver(PandasArchiver):

    def __init__(self, filename: PathLike, dao: Daos, sep: str = ";") -> None:

        super(CsvArchiver, self).__init__(dao)

        if not isinstance(filename, str):
            raise TypeError(f"{filename} is not a proper filename")

        self.filename = filename
        self.sep = sep

    def __write__(self) -> None:
        self.data.to_csv(self.filename, sep=self.sep)

    def __read__(self) -> pd.DataFrame:
        try:
            output = pd.read_csv(self.filename, sep=self.sep, index_col=0)
        except EmptyDataError:
            output = pd.DataFrame()
        return output


class PickleArchiver(PandasArchiver):

    def __init__(self, filename: PathLike, dao: Daos) -> None:

        super(PickleArchiver, self).__init__(dao)

        if not isinstance(filename, str):
            raise TypeError(f"{filename} is not a proper filename")

        self.filename = filename

    def __write__(self) -> None:
        self.data.to_pickle(self.filename)

    def __read__(self) -> pd.DataFrame:
        return pd.read_pickle(self.filename)


class TableArchiver(PandasArchiver):

    def __init__(self, table: Table, dao: Daos) -> None:
        super(TableArchiver, self).__init__(dao)

        assert isinstance(table, Table)
        self.table = table

    def __write__(self) -> None:
        self.table.write(self.data, overwrite=True)

    def __read__(self) -> pd.DataFrame:
        try:
            return self.table.data
        except IOError:
            return pd.DataFrame()
