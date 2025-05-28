from app.database.factories.role_factory import ROLE_DEFINITIONS, RoleFactory
from app.database.seeds import seed_actions
from app.database.seeds.base_seeder import FactorySeeder, ManagerSeeder
from app.managers import RoleManager


class Seeder(FactorySeeder, ManagerSeeder):
    def __init__(self):
        FactorySeeder.__init__(self, name='RoleSeeder', priority=0, factory=RoleFactory)
        ManagerSeeder.__init__(self, manager=RoleManager())

    @seed_actions
    def seed(self, rows: int = None) -> None:
        for role in ROLE_DEFINITIONS:
            if self.manager.find_by_name(role['name']) is None:
                self.factory.create(**role)
