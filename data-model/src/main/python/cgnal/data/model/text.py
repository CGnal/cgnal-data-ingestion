import numpy as np
import pandas as pd

import uuid

from cgnal.utils.dict import union, unflattenKeys
from cgnal.data.model.core import Iterable, LazyIterable, CachedIterable


def generate_random_uuid():
    return uuid.uuid1().bytes[:12]


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

    def removeProperty(self, key):
        return Document(self.uuid, {k: v for k, v in self.data.items() if k != key})

    def addProperty(self, key, value):
        return Document(self.uuid, union(self.data, unflattenKeys({key: value})))

    def setRandomUUID(self):
        return Document(generate_random_uuid(), self.data)

    @property
    def author(self):
        return self.getOrThrow('author')

    @property
    def text(self):
        return self.getOrThrow('text')

    @property
    def language(self):
        return self.getOrThrow('language')

    def __getitem__(self, item):
        return self.data[item]

    @property
    def properties(self):
        for prop in self.data.keys():
            yield prop

    def items(self):
        for prop in self.properties:
            yield prop, self[prop]

class Documents(Iterable):

    @property
    def documents(self):
        return self.items

    def __getitem__(self, item):
        return self.documents[item]

    def __iter__(self):
        for doc in self.documents:
            yield doc


class CachedDocuments(CachedIterable, Documents):

    @staticmethod
    def __get_key__(key, dict):
        try:
            out = dict
            for level in key.split("."):
                out = out[level]
            return out
        except:
            return np.nan

    def to_df(self, fields=[]):
        return pd.DataFrame.from_dict({doc.uuid: {field: self.__get_key__(field, doc.data)
                                                  for field in fields}
                                       for doc in self.documents}, orient='index')


class LazyDocuments(LazyIterable, Documents):

    @staticmethod
    def toCached(items):
        return CachedDocuments(list(items))


