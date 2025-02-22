from abc import ABC, abstractmethod

from app.extensions import db, ma
from app.managers import BaseManager


class BaseService(ABC):
    def __init__(self, manager: BaseManager, serializer: ma.SQLAlchemySchema, search_serializer: ma.Schema):
        self.manager = manager
        self.serializer = serializer
        self.search_serializer = search_serializer

    @abstractmethod
    def create(self, **kwargs) -> db.Model:
        raise NotImplementedError

    @abstractmethod
    def find(self, record_id: int, *args) -> db.Model | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, record_id: int, **kwargs) -> db.Model:
        raise NotImplementedError

    @abstractmethod
    def get(self, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def delete(self, record_id: int) -> db.Model:
        raise NotImplementedError
