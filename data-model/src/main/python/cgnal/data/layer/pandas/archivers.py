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
        """
        Create an in-memory archiver based on structured data stored as a pandas DataFrame

        :param dao: An instance of :class:`cgnal.data.layer.pandas.dao.DocumentDao/SeriesDAO/DataFrameDAO` that helps
            to retrieve/archive a pd.DataFrame row

        """
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
        """
        Retrive row from a dataframe by id

        :param uuid: row id
        :return: retrieved row parsed according to self.dao
        """
        row = self.data.loc[uuid]
        return self.dao.parse(row)

    def retrieve(self, condition: Optional[Callable[[pd.DataFrame], pd.DataFrame]] = None,
                 sort_by: Optional[Union[str, List[str]]] = None) -> Iterator[DataVal]:
        """
        Retrieve rows satisfying condition, sorted according to given ordering

        :param condition: condition to satisfy. If None return all rows.
        :param sort_by: ordering to respect. If None, no ordering is given.
        :return: iterator of (ordered) rows satisfying given condition
        """
        rows = self.data if condition is None else condition(self.data)
        rows = rows.sort_values(sort_by) if sort_by is not None else rows
        return (self.dao.parse(row) for _, row in rows.iterrows())

    def retrieveGenerator(self, condition: Optional[Callable[[pd.DataFrame], pd.DataFrame]] = None,
                          sort_by: Optional[Union[str, List[str]]] = None) -> IterGenerator[DataVal]:
        """
        Retrieve a generator of rows satisfying condition, sorted according to given ordering

        :param condition: condition to satisfy. If None return all rows.
        :param sort_by: ordering to respect. If None, no ordering is given.
        :return: generator of rows satisfying given condition. The generator is of the the type
            :class:`cgnal.data.model.core.IterGenerator` (ordered)
        """
        def __iterator__():
            return self.retrieve(condition=condition, sort_by=sort_by)
        return IterGenerator(__iterator__)

    def archiveOne(self, obj: DataVal):
        """
        Insert an object of type Document/pd.DataFrame/pd.Series in a pd.DataFrame

        :param obj: An instance of :class:`cgnal.data.model.text.Document, pd.DataFrame or pd.Series`
        :return: self i.e. an instance of ``PandasArchiver`` with updated self.data object

        """
        return self.archiveMany([obj])

    def archiveMany(self, objs: IterableType[DataVal]) -> 'PandasArchiver':
        """
        Insert many objects of type Document/pd.DataFrame/pd.Series in a pd.DataFrame

        :param objs: List of objects to be inserted. The objects can be of the following class instances
            :class:`cgnal.data.model.text.Document`, `pd.DataFrame` or `pd.Series`
        :return: self i.e. an instance of ``PandasArchiver`` with updated self.data object

        """
        def create_df(obj):
            s = self.dao.get(obj)
            s.name = self.dao.computeKey(obj)
            return s.to_frame().T

        new = pd.concat([create_df(obj) for obj in objs], sort=True)
        self.data = pd.concat([self.data.loc[set(self.data.index).difference(new.index)], new], sort=True)
        return self

    def archive(self, objs: Union[IterableType[DataVal], DataVal]):
        """
        Insert one or more objects in the underlying pd.DataFrame object.

        :param objs: object or list of objects to be archived. The objects can be of the
            :class:`cgnal.data.model.text.Document`, `pd.DataFrame` or `pd.Series`
        :return: self i.e. an instance of ``PandasArchiver`` with updated self.data object

        """
        if isinstance(objs, Iterable):
            return self.archiveMany(objs)
        else:
            return self.archiveOne(objs)


class CsvArchiver(PandasArchiver):

    def __init__(self, filename: PathLike, dao: Daos, sep: str = ";") -> None:
        """
        Create an in-memory archiver based on structured data stored in the filesystem as a CSV.

        :param filename: str, path object or file like object. Any valid string path to a csv file.
        :param dao: An instance of :class:`cgnal.data.layer.pandas.dao.DocumentDao/SeriesDAO/DataFrameDAO`
            that helps to retrieve/archive a `pd.Dataframe` row.
        :param sep: str, default ';'. Delimiter to use

        """

        super(CsvArchiver, self).__init__(dao)

        if not isinstance(filename, str):
            raise TypeError(f"{filename} is not a proper filename")

        self.filename = filename
        self.sep = sep

    def __write__(self) -> None:
        """
        Write object to a csv file

        :return: None
        """
        self.data.to_csv(self.filename, sep=self.sep)

    def __read__(self) -> pd.DataFrame:
        """
        Read csv file into a pandas DataFrame

        :return: pandas Dataframe
        """
        try:
            output = pd.read_csv(self.filename, sep=self.sep, index_col=0)
        except EmptyDataError:
            output = pd.DataFrame()
        return output


class PickleArchiver(PandasArchiver):

    def __init__(self, filename: PathLike, dao: Daos) -> None:
        """
        Create an in-memory archiver based on structured data stored in the filesystem as a Pickle.

        :param filename: str, path object or file like object. Any valid string path to a pickle file.
        :param dao: An instance of :class:`cgnal.data.layer.pandas.dao.DocumentDao/SeriesDAO/DataFrameDAO`
            that helps to retrieve/archive a `pd.Dataframe` row.

        """

        super(PickleArchiver, self).__init__(dao)

        if not isinstance(filename, str):
            raise TypeError(f"{filename} is not a proper filename")

        self.filename = filename

    def __write__(self) -> None:
        """
        Write object to a pickle file

        :return:
        """
        self.data.to_pickle(self.filename)

    def __read__(self) -> pd.DataFrame:
        """
        Read pickle file into a pandas Dataframe

        :return: pandas Dataframe
        """
        return pd.read_pickle(self.filename)


class TableArchiver(PandasArchiver):

    def __init__(self, table: Table, dao: Daos) -> None:
        """
        Create an in-memory archiver based on structured data stored as a table.

        :param table: An instance of :class:`cgnal.data.layer.pandas.databases.Table`
        :param dao: An instance of :class:`cgnal.data.layer.pandas.dao.DocumentDao/SeriesDAO/DataFrameDAO`
            that helps to retrieve/archive a `pd.Dataframe` row.

        """
        super(TableArchiver, self).__init__(dao)

        assert isinstance(table, Table)
        self.table = table

    def __write__(self) -> None:
        """
        Write Table object as a pickle file

        :return: None
        """
        self.table.write(self.data, overwrite=True)

    def __read__(self) -> pd.DataFrame:
        """
        Read object into a pandas Dataframe

        :return: pd.DataFrame
        """
        try:
            return self.table.data
        except IOError:
            return pd.DataFrame()
