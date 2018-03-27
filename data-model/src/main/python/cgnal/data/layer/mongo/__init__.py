from abc import ABCMeta, abstractmethod

from collections import Iterable

from pymongo.collection import Collection
from bson.objectid import ObjectId

from cgnal.data.layer import Archiver
from cgnal.data.model.core import IterGenerator

class MongoDAO(object):
    __metaclass__ = ABCMeta

    mapping = {}

    @property
    def inverse_mapping(self):
        return {v: k for k, v in self.mapping.items()}

    def translate(self, d):
        return {self.mapping.get(k, k): v for k, v in d.items()}

    def conversion(self, d):
        return {self.inverse_mapping.get(k, k): v for k, v in d.items()}

    @abstractmethod
    def computeKey(self, obj):
        raise NotImplementedError

    @abstractmethod
    def json(self, obj):
        raise NotImplementedError

    @abstractmethod
    def parse(self, json):
        raise NotImplementedError


class MongoArchiver(Archiver):
    def __init__(self, collection, dao):
        if not isinstance(collection, Collection):
            raise TypeError("Collection %s is not a MongoDb collection" % str(collection))

        self.collection = collection
        self.dao = dao

    def retrieveById(self, uuid):
        json = self.collection.find_one({"_id": ObjectId(uuid)})
        return self.dao.parse(json)

    def retrieve(self, condition={}):
        jsons = self.collection.find(condition)
        return (self.dao.parse(json) for json in jsons)

    def retrieveGenerator(self, condition={}):
        def __iterator__():
            return self.retrieve(condition=condition)
        return IterGenerator( __iterator__ )

    def archiveOne(self, obj):
        json = self.dao.json(obj)
        return self.collection.insert_one(json)

    def archiveMany(self, objs):
        return [self.collection.insert_one(self.dao.json(obj)) for obj in objs]

    def archive(self, objs):
        if isinstance(objs, Iterable):
            return self.archiveMany(objs)
        else:
            return self.archiveOne(objs)

    def map(self, f, condition={}):
        for obj in self.retrieve(condition):
            yield f(obj)

    def foreach(self, f, condition={}):
        for obj in self.retrieve(condition):
            f(obj)

    def first(self):
        json = self.collection.find_one()
        return self.dao.parse(json)

