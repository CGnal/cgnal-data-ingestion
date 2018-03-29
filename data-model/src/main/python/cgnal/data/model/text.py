import pandas as pd

from cgnal.utils.dict import union
from cgnal.data.model.core import Iterable, LazyIterable, CachedIterable

class Document(object):
    def __init__(self, uuid, data):
        self.uuid = uuid
        self.data = data

    def __str__(self):
        return "Id: %s" % self.uuid

    def getOrThrow(self, key, default=None):
        try:
            return self.data[key]
        except(KeyError) as e:
            if default is not None:
                return default
            else:
                raise e

    @staticmethod
    def fromKeyValueToDict(key, value):
        levels = key.split(".")
        out = value
        for level in reversed(levels):
            out = {level: out}
        return out

    def addProperty(self, key, value):
        return Document(self.uuid, union(self.data, self.fromKeyValueToDict(key, value)))

    @property
    def author(self):
        return self.getOrThrow('author')

    @property
    def text(self):
        return self.getOrThrow('text')

    @property
    def language(self):
        return self.getOrThrow('language')


class Documents(Iterable):

    @property
    def documents(self):
        return self.items

class CachedDocuments(CachedIterable, Documents):

    @staticmethod
    def __get_key__(key, dict):
        out = dict
        for level in key.split("."):
            out = out[level]
        return out

    def to_df(self, fields=[]):
        return pd.DataFrame.from_dict({doc.uuid: {field: self.__get_key__(field, doc.data)
                                                  for field in fields}
                                       for doc in self.documents}, orient='index')


class LazyDocuments(LazyIterable, Documents):

    @staticmethod
    def toCached(items):
        return CachedDocuments(list(items))


