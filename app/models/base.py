from abc import abstractmethod
from datetime import datetime
from typing import TypeVar

from ..extensions import db_wrapper as db

B = TypeVar('B', bound='BaseModel')


class Base(db.Model):
    class Meta:
        database = db.database

    @abstractmethod
    def save(self, *args: list, **kwargs: dict) -> int:
        if hasattr(self, 'created_at') and hasattr(self, 'deleted_at'):
            current_date = datetime.utcnow()

            if self.id is None and self.created_at is None:
                self.created_at = current_date

            if self.deleted_at is None:
                self.updated_at = current_date

        return super(Base, self).save(*args, **kwargs)

    @classmethod
    def get_fields(cls, exclude: list = None, include: list = None, sort_order: list = None) -> set:
        exclude = exclude or []
        include = include or []
        sort_order = sort_order or []

        fields = set(filter(
            lambda x: x not in exclude,
            list(cls._meta.fields)
        ))

        if include:
            fields = set(filter(
                lambda x: x in include,
                list(cls._meta.fields)
            ))

        if sort_order and len(fields) == len(sort_order):
            fields = sorted(fields, key=lambda x: sort_order.index(x))

        return fields
