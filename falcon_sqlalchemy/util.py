from sqlalchemy.orm import Session
from typing import List, Optional

from .types import IDType, ItemType

_default_config = dict(host='localhost',
                       port=r.DEFAULT_PORT,
                       db=None,
                       auth_key=None,
                       user='admin',
                       password=None,
                       timeout=20)


class SQLAlchemyMixin(object):
    _model = None

    def get_table(self, session: Session):
        return session.query(self._model)

    def list_items(self, n_items=100, session: Session = None) -> List[ItemType]:
        return self.get_table(session).limit(n_items).all()

    def get_item(self, item_id: IDType, session: Session) -> Optional[ItemType]:
        return self.get_table(session).get(item_id)

    def post_item(self, item: ItemType, session: Session) -> IDType:
        result = session.add(self._model(**item))
        session.commit()
        generated_key = result["generated_keys"][0]
        return generated_key

    def put_item(self, item_id: IDType, item: ItemType, session: Session) -> IDType:
        item[self._primary_key] = item_id
        self.get_table(session).insert(item, conflict="replace").run(conn)
        return item_id

    def update_item(self, item_id: IDType, partial_body: ItemType, session: Session) -> bool:
        result = self.get_table(session).get(item_id).update(partial_body).run(conn)
        ok = result["skipped"] == 0
        return ok

    def delete_item(self, item_id: IDType, session: Session) -> bool:
        result = self.get_table(session).get(item_id).delete().run(conn)
        ok = result["deleted"] == 1
        return ok
