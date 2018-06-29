import pandas as pd

from cgnal.data.model.text import Document
from cgnal.data.layer import DAO

class DocumentDAO(DAO):
    def computeKey(self, doc):
        return doc.uuid

    def get(self, doc):
        return pd.Series(doc.data, name=self.computeKey(doc))

    def parse(self, row):
        return Document(row.name, row.to_dict())

