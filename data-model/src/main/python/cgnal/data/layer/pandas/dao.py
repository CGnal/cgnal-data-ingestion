import json
import pandas as pd

from cgnal.data.model.text import Document
from cgnal.data.layer import DAO


class DocumentDAO(DAO):
    """Data access object for documents"""

    def computeKey(self, doc):
        return doc.uuid

    def get(self, doc):
        """Get doc as pd.Series with uuid as name"""
        return pd.Series(doc.data, name=self.computeKey(doc))

    def parse(self, row):
        return Document(row.name, row.to_dict())


class DataFrameDAO(DAO):
    """Data Access Object for pd.DataFrames"""

    def computeKey(self, df):
        try:
            return df.name
        except AttributeError:
            return hash(json.dumps({str(k): str(v) for k, v in df.to_dict().items()}))

    def get(self, df):
        return pd.concat({k: df[k] for k in df})

    def parse(self, row):
        return pd.concat({c: row[c] for c in row.index.levels[0]}, axis=1)

    @staticmethod
    def addName(df, name):
        df.name = name
        return df


class SeriesDAO(DAO):
    """Data Access Object for pd.Series"""

    def computeKey(self, df):
        return df.name

    def get(self, s):
        return s

    def parse(self, row):
        return row
