from cgnal.config import BaseConfig, AuthConfig

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
    @property
    def auth(self):
        return AuthConfig(self.sublevel("auth"))
    @property
    def admin(self):
        return AuthConfig(self.sublevel("admin"))
    @property
    def authSource(self):
        return self.safeGetValue("authSource")
