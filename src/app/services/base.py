from abc import ABC, abstractmethod

from app.extensions import db
from app.repositories.base import BaseRepository


class BaseService(ABC):
    def __init__(self, repository: BaseRepository):
        self.repository = repository


class CreationService(ABC):
    @abstractmethod
    def create(self, **kwargs) -> db.Model:
        raise NotImplementedError


class DeletionService(ABC):
    @abstractmethod
    def delete(self, record_id: int) -> db.Model:
        raise NotImplementedError


class FindByIdService(ABC):
    @abstractmethod
    def find_by_id(self, record_id: int, *args) -> db.Model | None:
        raise NotImplementedError


class GetService(ABC):
    @abstractmethod
    def get(self, **kwargs) -> dict:
        raise NotImplementedError


class SaveService(ABC):
    @abstractmethod
    def save(self, record_id: int, **kwargs) -> db.Model:
        raise NotImplementedError
