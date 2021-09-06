import json
import pandas as pd  # type: ignore

from typing import Hashable, Optional
from cgnal.data.model.text import Document
from cgnal.data.layer import DAO


class DocumentDAO(DAO):
    """Data access object for documents"""

    def computeKey(self, doc: Document) -> Hashable:
        return doc.uuid

    def get(self, doc: Document) -> pd.Series:
        """Get doc as pd.Series with uuid as name"""
        return pd.Series(doc.data, name=self.computeKey(doc))

    def parse(self, row: pd.Series) -> Document:
        return Document(row.name, row.to_dict())


class DataFrameDAO(DAO):
    """Data Access Object for pd.DataFrames"""

    def computeKey(self, df: pd.DataFrame) -> Hashable:
        try:
            return df.name
        except AttributeError:
            return hash(json.dumps({str(k): str(v) for k, v in df.to_dict().items()}))

    def get(self, df: pd.DataFrame) -> pd.Series:
        return pd.concat({k: df[k] for k in df})

    def parse(self, row: pd.DataFrame) -> pd.DataFrame:
        return pd.concat({c: row[c] for c in row.index.levels[0]}, axis=1)

    @staticmethod
    def addName(df: pd.DataFrame, name: Optional[Hashable]) -> pd.DataFrame:
        df.name = name
        return df


class SeriesDAO(DAO):
    """Data Access Object for pd.Series"""

    def computeKey(self, df: pd.Series) -> Hashable:
        return df.name

    def get(self, s: pd.Series) -> pd.Series:
        return s

    def parse(self, row: pd.Series) -> pd.Series:
        return row
