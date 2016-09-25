from wsgiref.simple_server import make_server

from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

import falcon
from falcon_sqlalchemy.resource import SQLRootResource, SQLItemResource

sqlurl = "mysql+pymysql://root:test@127.0.0.1:3306/testdb?charset=utf8mb4"
Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    age = Column(Integer)


class UserRootResource(SQLRootResource):
    model = User


api = falcon.API()
handler = UserRootResource(sqlurl=sqlurl)


resource_name = "user"
resource_path = "/{}/".format(resource_name)
api.add_route(resource_path, handler)
# api.add_route(resource_path + "{item_id}", MyItemHandler(rethinkdb_conf))

server = make_server("127.0.0.1", 8888, api)
server.serve_forever()
