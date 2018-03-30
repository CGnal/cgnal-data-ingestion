from cgnal.data.layer.mongo import MongoDAO

from cgnal.utils.dict import union
from cgnal.data.model.text import Document

from bson.objectid import ObjectId

class DocumentDAO(MongoDAO):

    mapping = {}

    @property
    def inverse_mapping(self):
        return {v: k for k, v in self.mapping.items()}

    def translate(self, d):
        return {self.mapping.get(k, k): v for k, v in d.items()}

    def conversion(self, d):
        return {self.inverse_mapping.get(k, k): v for k, v in d.items()}


    def __init__(self, uuid = "uuid"):
        self.uuid = uuid

    def computeKey(self, obj):
        return {"_id": ObjectId(obj.uuid)}

    # mapping = {
    #     "userId"   : "author",
    #     "createdAt": "timestamp",
    #     "_id"      : "uuid"
    # }

    def json(self, obj):
        return self.conversion(union(obj.data, self.computeKey(obj)))

    def parse(self, json):
        translated = self.translate(json)
        return Document(str(translated[self.uuid]), self.translate(json))