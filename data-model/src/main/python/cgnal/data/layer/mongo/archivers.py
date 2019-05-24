from collections import Iterable

from pymongo.collection import Collection
from bson.objectid import ObjectId

from cgnal.data.layer import Archiver
from cgnal.data.model.core import IterGenerator

class MongoArchiver(Archiver):
    def __init__(self, collection, dao):
        if not isinstance(collection, Collection):
            raise TypeError("Collection %s is not a MongoDb collection" % str(collection))

        self.collection = collection
        self.dao = dao

    def retrieveById(self, uuid):
        json = self.collection.find_one({"_id": ObjectId(uuid)})
        return self.dao.parse(json)

    def retrieve(self, condition={}, sort_by=None):
        jsons = self.collection.find(condition, no_cursor_timeout=True)
        if sort_by is not None:
            jsons = jsons.sort(sort_by)
        for json in jsons:
            yield self.dao.parse(json)
        jsons.close()

    def retrieveGenerator(self, condition={}, sort_by=None):
        def __iterator__():
            return self.retrieve(condition=condition, sort_by=sort_by)
        return IterGenerator( __iterator__ )

    def archiveOne(self, obj):
        return self.__insert__(obj)

    def __insert__(self, obj):
        return self.collection.update_one(self.dao.computeKey( obj ),
                                          {"$set": self.dao.get(obj)}, upsert=True)

    def archiveMany(self, objs):
        return [self.__insert__(obj) for obj in objs]

    def archive(self, objs):
        if isinstance(objs, Iterable):
            return self.archiveMany(objs)
        else:
            return self.archiveOne(objs)

    def first(self):
        json = self.collection.find_one()
        return self.dao.parse(json)

