from app.database.factories.role_factory import RoleFactory
from app.database.seeds import seed_actions
from app.database.seeds.base_seeder import FactorySeeder, ManagerSeeder
from app.managers import RoleManager

ROLE_DEFINITIONS = [
    {'name': 'admin', 'description': 'Administrator', 'label': 'Admin'},
    {'name': 'team_leader', 'description': 'Team leader', 'label': 'Team leader'},
    {'name': 'worker', 'description': 'Worker', 'label': 'Worker'},
]


class Seeder(FactorySeeder, ManagerSeeder):
    def __init__(self):
        FactorySeeder.__init__(self, name='RoleSeeder', priority=0, factory=RoleFactory)
        ManagerSeeder.__init__(self, manager=RoleManager())

    @seed_actions
    def seed(self):
        for role in ROLE_DEFINITIONS:
            if self.manager.find_by_name(role['name']) is None:
                self.factory.create(**role)
