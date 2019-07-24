from cgnal.config import BaseConfig

class MongoConfig(BaseConfig):
    @property
    def host(self):
        return self.getValue("host")
    @property
    def port(self):
        return self.getValue("port")
    @property
    def db_name(self):
        return self.getValue("db_name")
    def getCollection(self, name):
        return self.config["collections"][name]
