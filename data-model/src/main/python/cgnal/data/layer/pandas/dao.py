import json
import pandas as pd
# type: ignore

from typing import Hashable, Optional
from cgnal.data.model.text import Document
from cgnal.data.layer import DAO


class DocumentDAO(DAO[Document, pd.Series]):
    """Data access object for documents"""

    def computeKey(self, doc: Document) -> Hashable:
        """
        Get document id

        :param doc: an instance of :class:`cgnal.data.model.text.Document`
        :return: uuid i.e. id of the given document
        """
        return doc.uuid

    def get(self, doc: Document) -> pd.Series:
        """
        Get doc as pd.Series with uuid as name

        :param doc: an instance of :class:`cgnal.data.model.text.Document`
        :return: pd.Series
        """
        return pd.Series(doc.data, name=self.computeKey(doc))

    def parse(self, row: pd.Series) -> Document:
        """
        Get a row i.e. pd.Series as a Document

        :param row: pd.Series, row of a pd.DataFrame
        :return: :class:`cgnal.data.model.text.Document`, a Document object
        """
        from typing import Dict, Any
        data: Dict = row.to_dict() # type: ignore
        return Document(row.name, data)


class DataFrameDAO(DAO[pd.DataFrame, pd.Series]):
    """Data Access Object for pd.DataFrames"""

    def computeKey(self, df: pd.DataFrame) -> Hashable:
        """
        Get dataframe name

        :param df: pd.DataFrame. A pandas dataframe
        :return: str, name of the dataframe
        """
        try:
            return df.name
        except AttributeError:
            return hash(json.dumps({str(k): str(v) for k, v in df.to_dict().items()})) # type: ignore

    def get(self, df: pd.DataFrame) -> pd.Series:
        """
        Get dataframe as pd.Series

        :param df: pd.DataFrame. A pandas dataframe
        :return: pd.Series
        """
        return pd.concat({k: df[k] for k in df})

    def parse(self, row: pd.Series) -> pd.DataFrame:
        """
        Get a row i.e. pd.Series as a pandas DataFrame

        :param row: pd.Series, row of a pd.DataFrame
        :return: pd.DataFrame, a pandas dataframe object
        """
        if isinstance(row.index, pd.MultiIndex):
            return pd.concat({c: row[c] for c in row.index.levels[0]}, axis=1) # type: ignore
        else:
            return row.to_frame()

    @staticmethod
    def addName(df: pd.DataFrame, name: Optional[Hashable]) -> pd.DataFrame:
        """
        Adds name to the input dataframe

        :param df: pd.DataFrame
        :param name: str
        :return: pd.DataFrame
        """
        df.name = name
        return df


class SeriesDAO(DAO[pd.Series, pd.Series]):
    """Data Access Object for pd.Series"""

    def computeKey(self, df: pd.Series) -> Hashable:
        """
        Get series name

        :param df: pd.Series
        :return: str, name of the pandas series
        """
        return df.name

    def get(self, s: pd.Series) -> pd.Series:
        """
        Get a series as series object

        :param s: pd.Series
        :return: pd.Series
        """
        return s

    def parse(self, row: pd.Series) -> pd.Series:
        """
        Get a row as a pd.Series object

        :param row: pd.Series
        :return: pd.Series
        """
        return row
