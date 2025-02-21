import sqlalchemy as sa
from sqlalchemy import func

from app.extensions import db


class BaseMixin:
    __abstract__ = True
    id = sa.Column(sa.Integer, nullable=False, primary_key=True)

    created_at = sa.Column(sa.TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = sa.Column(sa.TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = sa.Column(sa.TIMESTAMP, nullable=True)


class Base(db.Model, BaseMixin):
    __abstract__ = True

    def reload(self):
        db.session.refresh(self)
        return self
