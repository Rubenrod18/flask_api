from abc import abstractmethod
from datetime import UTC, datetime

from sqlalchemy import event, func
import sqlalchemy as sa
from sqlalchemy.orm import validates

from app.extensions import db


class BaseMixin:
    __abstract__ = True
    id = sa.Column(sa.Integer, nullable=False, primary_key=True)

    created_at = sa.Column(sa.Integer, server_default=func.now(), nullable=False)
    updated_at = sa.Column(sa.Integer, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = sa.Column(sa.Integer, nullable=True)

    @validates('created_at', 'updated_at', 'deleted_at')
    def convert_datetime(self, key, value):
        if isinstance(value, datetime):
            return int(value.timestamp())
        return value

    def get_created_at(self):
        return datetime.fromtimestamp(self.created_at) if self.created_at else None

    def get_updated_at(self):
        return datetime.fromtimestamp(self.updated_at) if self.updated_at else None

    def get_deleted_at(self):
        return datetime.fromtimestamp(self.deleted_at) if self.deleted_at else None


@event.listens_for(db.session, 'before_flush')
def before_flush(session, flush_context, instances):
    for instance in session.dirty:
        if isinstance(instance, BaseMixin):  # Ensure we're working with the right model
            if instance.id and instance.updated_at:
                instance.updated_at = int(datetime.now(UTC).timestamp())  # Set updated_at before flush

            elif not instance.id:  # New record
                if not instance.created_at:
                    instance.created_at = int(datetime.now(UTC).timestamp())  # Set created_at if it's not set yet
                if not instance.updated_at:
                    instance.updated_at = instance.created_at  # Set updated_at to created_at initially


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
