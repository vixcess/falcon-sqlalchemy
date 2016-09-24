from sqlalchemy import Column, Integer
from sqlalchemy.orm import Session
from typing import List, Optional

from .types import IDType, ItemType


class PrimaryKeyMixin(object):
    id = Column(Integer, primary_key=True)


class SQLAlchemyMixin(object):
    model = None

    def __init__(self):
        if self.model is None:
            raise ValueError("model not specified")

    def get_table(self, session: Session):
        return session.query(self.model)

    def list_items(self, n_items=100, session: Session = None) -> List[ItemType]:
        return self.get_table(session).limit(n_items).all()

    def get_item(self, item_id: IDType, session: Session) -> Optional[ItemType]:
        return self.get_table(session).get(item_id)

    def post_item(self, item: ItemType, session: Session) -> IDType:
        session.add(self.model(**item))
        session.commit()
        return self.model.id

    def put_item(self, item_id: IDType, item: ItemType, session: Session) -> IDType:
        session.merge(self.model(id=item_id, **item))
        session.commit()
        return item_id

    def update_item(self, item_id: IDType, partial_body: ItemType, session: Session) -> bool:
        item = self.get_item(item_id, session)
        if item is None:
            return False
        for (k, v) in partial_body.items():
            setattr(item, k, v)
        session.merge(item)
        session.commit()
        return True

    def delete_item(self, item_id: IDType, session: Session) -> bool:
        item = self.get_item(item_id, session)
        if item is None:
            return False
        session.delete(item)
        session.commit()
        return True
