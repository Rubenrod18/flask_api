from app.database.factories.role_factory import ROLE_DEFINITIONS, RoleFactory
from app.database.seeds import seed_actions
from app.database.seeds.base_seeder import FactorySeeder, RepositorySeeder
from app.repositories import RoleRepository


class Seeder(FactorySeeder, RepositorySeeder):
    def __init__(self):
        FactorySeeder.__init__(self, name='RoleSeeder', priority=0, factory=RoleFactory)
        RepositorySeeder.__init__(self, repository=RoleRepository())

    @seed_actions
    def seed(self, rows: int = None) -> None:
        for role in ROLE_DEFINITIONS:
            if self.repository.find_by_name(role['name']) is None:
                self.factory.create(**role)
