from abc import ABC
from datetime import datetime, UTC

from flask_sqlalchemy.model import DefaultMeta

from app.extensions import db


class BaseRepository(ABC):
    def __init__(self, model: type[DefaultMeta]):
        self.model = model

    def create(self, **kwargs) -> db.Model:
        raise NotImplementedError

    def find(self, *args, **kwargs) -> db.Model | None:
        raise NotImplementedError

    def delete(self, record: db.Model, force_delete: bool = False) -> db.Model | int:
        raise NotImplementedError


class MySQLRepository(BaseRepository):
    def __init__(self, model: type[DefaultMeta]):
        super().__init__(model=model)

    def create(self, **kwargs) -> db.Model:
        return self.model(**kwargs)

    def find(self, *args, **kwargs) -> db.Model | None:
        return db.session.query(self.model).filter(*args).first()

    def delete(self, record: db.Model, force_delete: bool = False) -> db.Model | int:
        if force_delete:
            raise NotImplementedError
        else:
            record.deleted_at = datetime.now(UTC)

        return record
