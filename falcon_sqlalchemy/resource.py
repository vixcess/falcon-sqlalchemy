import falcon
import rethinkdb as r
from falcon import Request, Response

from . import hooks
from .types import JSONType
from .util import RethinkDBMixin, parse_rethinkdb_url


def put_json_to_context(req: Request, item: JSONType, key="result"):
    req.context[key] = item


class _RethinkDBResource(RethinkDBMixin):
    schema = None

    def __init__(self, conf_or_url):
        # check if tablename is defines
        if self._table_name is None:
            raise ValueError("table name not defined")

        if isinstance(conf_or_url, str):
            self._rethinkdb_conf = parse_rethinkdb_url(conf_or_url)
        else:
            self._rethinkdb_conf = conf_or_url

    def get_conn(self) -> r.Connection:
        return r.connect(**self._rethinkdb_conf)

    @property
    def conn(self):
        return self.get_conn()

    def init_db(self):
        conn = self.conn
        self.create_table(conn)
        self.create_indices(conn)


@falcon.after(hooks.dump_json)
class RethinkDBRootResource(_RethinkDBResource):
    def on_get(self, req: Request, res: Response):
        items = self.list_items(self.conn)
        put_json_to_context(req, items)

    @falcon.before(hooks.require_json)
    @falcon.before(hooks.parse_json)
    @falcon.before(hooks.validate_json)
    def on_post(self, req: Request, res: Response):
        item_id = self.post_item(req.context["doc"], self.conn)
        put_json_to_context(req, {"created": item_id})


@falcon.after(hooks.dump_json)
class RethinkDBItemResource(_RethinkDBResource):
    def on_get(self, req: Request, res: Response, item_id):
        item = self.get_item(item_id, self.conn)
        if item is None:
            raise falcon.HTTPNotFound()
        put_json_to_context(req, item)

    @falcon.before(hooks.require_json)
    @falcon.before(hooks.parse_json)
    @falcon.before(hooks.validate_json)
    def on_put(self, req: Request, res: Response, item_id):
        self.put_item(item_id, req.context["doc"], self.conn)
        put_json_to_context(req, {"created": item_id})

    @falcon.before(hooks.require_json)
    @falcon.before(hooks.parse_json)
    def on_patch(self, req: Request, res: Response, item_id):
        ok = self.update_item(item_id, req.context["doc"], self.conn)
        if not ok:
            raise falcon.HTTPNotFound()

    def on_delete(self, req: Request, res: Response, item_id):
        ok = self.delete_item(item_id, self.conn)
        if not ok:
            raise falcon.HTTPNotFound()
