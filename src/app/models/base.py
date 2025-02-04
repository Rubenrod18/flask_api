from abc import abstractmethod
from datetime import UTC, datetime

from sqlalchemy import event, func
import sqlalchemy as sa
from sqlalchemy.orm import validates

from app.extensions import db


class BaseMixin:
    __abstract__ = True
    id = sa.Column(sa.Integer, nullable=False, primary_key=True)

    created_at = sa.Column(sa.TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = sa.Column(sa.TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = sa.Column(sa.TIMESTAMP, nullable=True)


class Base(db.Model, BaseMixin):
    __abstract__ = True

    @classmethod
    def get_fields(
        cls, exclude: list = None, include: list = None, sort_order: list = None
    ) -> set:
        exclude = exclude or []
        include = include or []
        sort_order = sort_order or []
        column_names = [c.name for c in cls.__table__.columns]

        fields = set(filter(lambda x: x not in exclude, column_names))

        if include:
            fields = set(filter(lambda x: x in include, column_names))

        if sort_order and len(fields) == len(sort_order):
            fields = sorted(fields, key=lambda x: sort_order.index(x))

        return fields

    @staticmethod
    def raw(query: str):
        return db.session.execute(sa.text(query))

    def reload(self):
        db.session.refresh(self)
        return self
