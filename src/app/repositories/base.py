from abc import ABC

from flask_sqlalchemy.model import DefaultMeta

from app.extensions import db


class BaseRepository(ABC):
    def __init__(self, model: type[DefaultMeta]):
        self.model = model

    def create(self, **kwargs) -> db.Model:
        raise NotImplementedError

    def find(self, *args, **kwargs) -> db.Model | None:
        raise NotImplementedError


class MySQLRepository(BaseRepository):
    def __init__(self, model: type[DefaultMeta]):
        super().__init__(model)

    def create(self, **kwargs) -> db.Model:
        return self.model(**kwargs)

    def find(self, *args, **kwargs) -> db.Model | None:
        return db.session.query(self.model).filter(*args).first()
