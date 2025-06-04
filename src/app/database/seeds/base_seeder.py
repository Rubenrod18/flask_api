from abc import ABC

from app.database.factories.base_factory import BaseFactory
from app.database.seeds import seed_actions
from app.repositories.base import BaseRepository


class BaseSeeder(ABC):
    def __init__(self, name: str, priority: int):
        self.name = name
        self.priority = priority

    @seed_actions
    def seed(self, rows: int = None):
        raise NotImplementedError


class FactorySeeder(BaseSeeder):
    def __init__(self, name: str, priority: int, factory: type[BaseFactory]):
        super().__init__(name, priority)
        self.factory = factory


class RepositorySeeder:
    """

    NOTE: Instead of both FactorySeeder and RepositorySeeder inheriting BaseSeeder, make RepositorySeeder a mixin that
    adds the repository attribute. This change avoid Python’s MRO (Method Resolution Order) will try to call BaseSeeder
    twice (once for FactorySeeder and once for RepositorySeeder) if RepositorySeeder inherits BaseSeeder.

    """

    def __init__(self, repository: BaseRepository):
        self.repository = repository
