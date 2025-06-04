from abc import ABC, abstractmethod

from app.extensions import db
from app.repositories.base import BaseRepository


class BaseService(ABC):
    def __init__(self, repository: BaseRepository):
        self.repository = repository

    @abstractmethod
    def create(self, **kwargs) -> db.Model:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, record_id: int, *args) -> db.Model | None:
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
