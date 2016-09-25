import falcon
from falcon import Request, Response
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError

from . import hooks
from .types import JSONType
from .util import SQLAlchemyMixin, AutoCloseSessionMaker


def put_json_to_context(req: Request, item: JSONType, key="result"):
    req.context[key] = item


class _SQLResource(SQLAlchemyMixin):
    schema = None

    def __init__(self, sqlurl, **kwargs):
        super().__init__()
        self._sqlurl = sqlurl
        self._engine = create_engine(sqlurl)
        self._session_maker = AutoCloseSessionMaker(bind=self._engine, **kwargs)

    def make_session(self, **kwds):
        return self._session_maker(**kwds)


@falcon.after(hooks.dump_json)
class SQLRootResource(_SQLResource):
    def on_get(self, req: Request, res: Response):
        with self.make_session() as session:
            items = self.list_items(session=session)
            put_json_to_context(req, items)

    @falcon.before(hooks.require_json)
    @falcon.before(hooks.parse_json)
    @falcon.before(hooks.validate_json)
    def on_post(self, req: Request, res: Response):
        with self.make_session() as session:
            try:
                item_id = self.post_item(req.context["doc"], session)
                put_json_to_context(req, {"created": item_id})
            except IntegrityError as e:
                raise falcon.HTTPConflict("Conflict", str(e))


@falcon.after(hooks.dump_json)
class SQLItemResource(_SQLResource):
    def on_get(self, req: Request, res: Response, item_id):
        with self.make_session() as session:
            item = self.get_item(item_id, session)
            if item is None:
                raise falcon.HTTPNotFound()
            put_json_to_context(req, item)

    @falcon.before(hooks.require_json)
    @falcon.before(hooks.parse_json)
    @falcon.before(hooks.validate_json)
    def on_put(self, req: Request, res: Response, item_id):
        with self.make_session() as session:
            try:
                self.put_item(item_id, req.context["doc"], session)
                put_json_to_context(req, {"created": item_id})
            except IntegrityError as e:
                raise falcon.HTTPConflict("Conflict", str(e))

    @falcon.before(hooks.require_json)
    @falcon.before(hooks.parse_json)
    def on_patch(self, req: Request, res: Response, item_id):
        with self.make_session() as session:
            try:
                ok = self.update_item(item_id, req.context["doc"], session)
                if not ok:
                    raise falcon.HTTPNotFound()
            except IntegrityError as e:
                raise falcon.HTTPConflict("Conflict", str(e))

    def on_delete(self, req: Request, res: Response, item_id):
        with self.make_session() as session:
            ok = self.delete_item(item_id, session)
            if not ok:
                raise falcon.HTTPNotFound()
