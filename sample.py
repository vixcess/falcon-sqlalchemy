from wsgiref.simple_server import make_server

from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

import falcon
from falcon_sqlalchemy import SQLRootResource, SQLItemResource
from falcon_sqlalchemy.util import IntegerPrimaryKeyMixin, StringPrimaryKeyMixin, DictableMixin

# sqlurl = "mysql+pymysql://root:test@127.0.0.1:3306/testdb?charset=utf8mb4"
sqlurl = "postgresql://root:test@127.0.0.1:5432/test"
Base = declarative_base()


class User(Base, IntegerPrimaryKeyMixin, DictableMixin):
    __tablename__ = "user"
    name = Column(String(64), unique=True)
    age = Column(Integer)


class UserRootHandler(SQLRootResource):
    model = User


class UserItemHandler(SQLItemResource):
    model = User


class User2(Base, StringPrimaryKeyMixin, DictableMixin):
    __tablename__ = "user2"
    name = Column(String(64), unique=True)
    age = Column(Integer)


class User2RootHandler(SQLRootResource):
    model = User2


class User2ItemHandler(SQLItemResource):
    model = User2


engine = create_engine(sqlurl)
Base.metadata.create_all(bind=engine)

api = falcon.API()

resource_name = "user"
resource_path = "/{}/".format(resource_name)
api.add_route(resource_path, UserRootHandler(sqlurl=sqlurl))
api.add_route(resource_path + "{item_id}", UserItemHandler(sqlurl=sqlurl))

resource_name = "user2"
resource_path = "/{}/".format(resource_name)
api.add_route(resource_path, User2RootHandler(sqlurl=sqlurl))
api.add_route(resource_path + "{item_id}", User2ItemHandler(sqlurl=sqlurl))

server = make_server("127.0.0.1", 8888, api)
server.serve_forever()
