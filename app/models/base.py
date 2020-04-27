from abc import abstractmethod
from datetime import datetime
from typing import TypeVar

from ..extensions import db_wrapper as db

B = TypeVar('B', bound='BaseModel')

class BaseModel(db.Model):
    @abstractmethod
    def save(self, *args: list, **kwargs: dict) -> int:
        current_date = datetime.utcnow()

        if self.id is None:
            self.created_at = current_date

        if self.deleted_at is None:
            self.updated_at = current_date

        return super(BaseModel, self).save(*args, **kwargs)

    @abstractmethod
    def serialize(self, ignore_fields: list = None) -> dict:
        pass

    @classmethod
    @abstractmethod
    def get_fields(self, ignore_fields: list = None) -> set:
        if ignore_fields is None:
            ignore_fields = []

        return set(
            filter(
                lambda x: x not in ignore_fields,
                list(self._meta.fields)
            )
        )

    @classmethod
    @abstractmethod
    def fake(self) -> B:
        pass

    @classmethod
    @abstractmethod
    def seed(self) -> None:
        pass