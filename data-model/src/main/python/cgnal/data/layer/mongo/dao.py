from bson.objectid import ObjectId  # type: ignore
import pandas as pd  # type: ignore

from typing import Dict, Union, Generic, TypeVar, Hashable
from cgnal.typing import T
from cgnal.data.layer import DAO
from cgnal.utils.dict import union
from cgnal.data.model.text import Document

K = TypeVar('K', Hashable, Hashable)
V = TypeVar('V', Hashable, Hashable)


class DocumentDAO(DAO, Generic[K, V]):

    mapping: Dict[K, V] = {}

    @property
    def inverse_mapping(self) -> Dict[V, K]:
        """
        Apply inverse of self.mapping

        :return: dictionary with self.mapping.keys as values and self.mapping.values as keys
        """
        return {v: k for k, v in self.mapping.items()}

    def translate(self, d: Dict[K, T]) -> Dict[Union[K, V], T]:
        """
        Map dictionary keys according to self.mapping

        :param d: dict to map
        :return: dictionary with mapped keys
        """
        return {self.mapping.get(k, k): v for k, v in d.items()}

    def conversion(self, d: Dict[V, T]) -> Dict[Union[K, V], T]:
        """
        Map dictionary keys according to the inverse of self.mapping

        :param d: dict to map
        :return: dictionary with mapped keys
        """
        return {self.inverse_mapping.get(k, k): v for k, v in d.items()}

    def __init__(self, uuid: str = "_id") -> None:
        self.uuid = uuid

    # TODO the output value of this method is a bit inconsistent with the one of following class (SeriesDao) and
    #  the one of pandas.dao.DocumentDAO. Wouldn't it be better for computeKey method to have the same signature for all
    #  DAOs (in all modules), defined in DAO ABC, as something on the line of
    #  def computeKey(self, obj: DataVal) -> Hashable
    #  where DataVal = TypeVar('DataVal', Document, pd.DataFrame, pd.Series)?
    def computeKey(self, obj: Document) -> Dict[str, ObjectId]:
        """
        Get document id as dictionary

        :param obj: document whose id is to retrieve
        :return: dictionary with '_id' key and ObjectId as value
        """
        return {"_id": ObjectId(obj.uuid)}

    def get(self, obj: Document) -> Dict[Union[K, V], T]:
        return self.conversion(union(obj.data, self.computeKey(obj)))

    def parse(self, json: Dict[K, T]) -> Document:
        translated = self.translate(json)
        return Document(str(translated[self.uuid]), self.translate(json))


class SeriesDAO(DAO):
    def __init__(self, key_field: str = "_id") -> None:
        self.key_field = key_field

    def computeKey(self, serie: pd.Series) -> Dict[str, ObjectId]:
        return {self.key_field: ObjectId(serie.name)}

    def get(self, serie: pd.Series) -> Dict[K, V]:
        return serie.to_dict()

    def parse(self, json: Dict[K, V]) -> pd.Series:
        s = pd.Series(json)
        s.name = s.pop(self.key_field)
        return s
