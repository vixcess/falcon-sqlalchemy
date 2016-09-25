from datetime import datetime
from typing import List, Optional
import uuid

from sqlalchemy import Column, BigInteger, String, DateTime
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql import functions as sqlfunc

from .types import IDType, ItemType


def _uuid():
    return str(uuid.uuid4())


class AutoCloseSession(Session):
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        try:
            if self.is_active:
                self.commit()
        except Exception as e:
            self.rollback()
            raise e
        finally:
            self.close()


class AutoCloseSessionMaker(sessionmaker):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.class_ = AutoCloseSession

    def __call__(self, **local_kw) -> AutoCloseSession:
        s = super().__call__(**local_kw)
        return s


class IntegerPrimaryKeyMixin(object):
    id = Column(BigInteger, primary_key=True)


class StringPrimaryKeyMixin(object):
    id = Column(String(64), primary_key=True, default=_uuid)


class CreatedAtMixin(object):
    created_at = Column(DateTime, nullable=False,
                        server_default=sqlfunc.now())


class UpdatedAtMixin(object):
    updated_at = Column(DateTime, nullable=False,
                        server_default=sqlfunc.now(),
                        onupdate=sqlfunc.now())


class DictableMixin(object):
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class SQLAlchemyMixin(object):
    model = None

    def __init__(self):
        if self.model is None:
            raise ValueError("model not specified")

    def get_table(self, session: Session):
        return session.query(self.model)

    def list_items(self, n_items=100, session: Session = None) -> List[DictableMixin]:
        return self.get_table(session).limit(n_items).all()

    def get_item(self, item_id: IDType, session: Session) -> Optional[DictableMixin]:
        return self.get_table(session).get(item_id)

    def post_item(self, item: ItemType, session: Session) -> IDType:
        item = self.model(**item)
        session.add(item)
        session.commit()
        return item.id

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
