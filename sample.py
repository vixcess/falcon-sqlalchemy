from wsgiref.simple_server import make_server

import falcon
from falcon_sqlalchemy import RethinkDBRootResource, RethinkDBItemResource
import rethinkdb as r

api = falcon.API()

resource_name = "myresource"

rethinkdb_conf = {}


class MyResource(object):
    _table_name = resource_name


class MyRootHandler(MyResource, RethinkDBRootResource):
    pass


class MyItemHandler(MyResource, RethinkDBItemResource):
    pass


resource_path = "/{}/".format(resource_name)
api.add_route(resource_path, MyRootHandler(rethinkdb_conf))
api.add_route(resource_path + "{item_id}", MyItemHandler(rethinkdb_conf))

MyRootHandler(rethinkdb_conf).init_db()

server = make_server("127.0.0.1", 8888, api)
server.serve_forever()
