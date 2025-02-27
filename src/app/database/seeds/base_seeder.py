from abc import ABC

from app.database.factories.base_factory import BaseFactory
from app.database.seeds import seed_actions
from app.managers import BaseManager


class BaseSeeder(ABC):
    def __init__(self, name: str, priority: int):
        self.name = name
        self.priority = priority

    @seed_actions
    def seed(self, *args, **kwargs):
        raise NotImplementedError


class FactorySeeder(BaseSeeder):
    def __init__(self, name: str, priority: int, factory: type[BaseFactory]):
        super().__init__(name, priority)
        self.factory = factory


class ManagerSeeder:
    """

    NOTE: Instead of both FactorySeeder and ManagerSeeder inheriting BaseSeeder, make ManagerSeeder a mixin that
    adds the manager attribute. This change avoid Python’s MRO (Method Resolution Order) will try to call BaseSeeder
    twice (once for FactorySeeder and once for ManagerSeeder) if ManagerSeeder inherits BaseSeeder.

    """

    def __init__(self, manager: BaseManager):
        self.manager = manager
