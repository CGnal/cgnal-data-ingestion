import uuid
import numpy as np  # type: ignore
import pandas as pd  # type: ignore

from typing import Dict, Any, Union, Optional, Iterator, Tuple, Iterable as IterableType, List, Mapping, Hashable
from cgnal.utils.dict import union, unflattenKeys
from cgnal.data.model.core import Iterable, LazyIterable, CachedIterable


def generate_random_uuid() -> bytes:
    return uuid.uuid1().bytes[:12]


# TODO: shouldn't uuid be just a string? If so the usage of setRandomUUID is not coherent since generate_random_uuid
#  does not return a string
class Document(object):
    def __init__(self, uuid: Hashable, data: Dict[str, Any]):
        self.uuid = uuid
        self.data = data

    def __str__(self) -> str:
        return f"Id: {self.uuid}"

    def getOrThrow(self, key: str, default: Any = None) -> Any:
        try:
            return self.data[key]
        except KeyError as e:
            if default is not None:
                return default
            else:
                raise e

    def removeProperty(self, key: str) -> 'Document':
        return Document(self.uuid, {k: v for k, v in self.data.items() if k != key})

    def addProperty(self, key: str, value: Any) -> 'Document':
        return Document(self.uuid, union(self.data, unflattenKeys({key: value})))

    def setRandomUUID(self) -> 'Document':
        return Document(generate_random_uuid(), self.data)

    @property
    def author(self) -> Optional[str]:
        return self.getOrThrow('author')

    @property
    def text(self) -> Optional[str]:
        return self.getOrThrow('text')

    @property
    def language(self) -> Optional[str]:
        return self.getOrThrow('language')

    def __getitem__(self, item: str) -> Any:
        return self.data[item]

    @property
    def properties(self) -> Iterator[str]:
        for prop in self.data.keys():
            yield prop

    def items(self) -> Iterator[Tuple[str, Any]]:
        for prop in self.properties:
            yield prop, self[prop]


# TODO: Documents.documents returns an IterableType, inherited directly from cgnal.data.ml.core.Iterable class. This is
#  not compatible with the requirement expressed in Documents.__getitem__ method that requires that Documents.documents
#  output. Should this class be an ABC, documents method could be made abstract and instantiated appropriately in its
#  descendants
class Documents(Iterable[Document]):

    @property
    def documents(self) -> IterableType[Document]:
        return self.items

    def __getitem__(self, item: Union[int, slice]) -> Document:
        return self.documents[item]

    def __iter__(self) -> Iterator[Document]:
        for doc in self.documents:
            yield doc


class CachedDocuments(CachedIterable, Documents):

    @staticmethod
    def __get_key__(key: str, dict: Dict[str, Any]) -> Any:
        try:
            out = dict
            for level in key.split("."):
                out = out[level]
            return out
        except (KeyError, AttributeError):
            return np.nan

    def to_df(self, fields: List[str] = []) -> pd.DataFrame:
        return pd.DataFrame.from_dict({doc.uuid: {field: self.__get_key__(field, doc.data)
                                                  for field in fields}
                                       for doc in self.documents}, orient='index')


class LazyDocuments(LazyIterable, Documents):

    @staticmethod
    def toCached(items: IterableType[Document]) -> CachedDocuments:
        return CachedDocuments(list(items))


