from cgnal.data.layer.mongo import MongoDAO

from cgnal.utils.dict import union
from cgnal.data.model.text import Document

from bson.objectid import ObjectId

class DocumentDAO(MongoDAO):
    def __init__(self):
        pass

    def computeKey(self, obj):
        return ObjectId(obj.uuid)

    mapping = {
        "userId": "author",
        "createdAt": "timestamp",
    }

    def json(self, obj):
        return self.conversion(union(obj.data, {"_id": self.computeKey(obj)}))

    def parse(self, json):
        return Document(str(json["_id"]), self.translate(json))