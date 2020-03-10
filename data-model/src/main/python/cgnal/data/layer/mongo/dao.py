from bson.objectid import ObjectId
import pandas as pd

from cgnal.data.layer import DAO

from cgnal.utils.dict import union
from cgnal.data.model.text import Document


class DocumentDAO(DAO):

    mapping = {}

    @property
    def inverse_mapping(self):
        return {v: k for k, v in self.mapping.items()}

    def translate(self, d):
        return {self.mapping.get(k, k): v for k, v in d.items()}

    def conversion(self, d):
        return {self.inverse_mapping.get(k, k): v for k, v in d.items()}

    def __init__(self, uuid="_id"):
        self.uuid = uuid

    def computeKey(self, obj):
        return {"_id": ObjectId(obj.uuid)}

    def get(self, obj):
        return self.conversion(union(obj.data, self.computeKey(obj)))

    def parse(self, json):
        translated = self.translate(json)
        return Document(str(translated[self.uuid]), self.translate(json))


class SeriesDAO(DAO):
    def __init__(self, key_field="_id"):
        self.key_field = key_field

    def computeKey(self, serie):
        return {self.key_field: ObjectId(serie.name)}

    def get(self, serie):
        return serie.to_dict()

    def parse(self, json):
        s = pd.Series(json)
        s.name = s.pop(self.key_field)
        return s
