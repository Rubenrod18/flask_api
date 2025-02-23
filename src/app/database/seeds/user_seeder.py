import os

from app.database.factories.user_factory import UserFactory
from app.database.seeds import seed_actions
from app.database.seeds.base_seeder import FactorySeeder, ManagerSeeder
from app.managers import RoleManager, UserManager
from app.models import User


class Seeder(FactorySeeder, ManagerSeeder):
    def __init__(self):
        FactorySeeder.__init__(self, name='UserSeeder', priority=1, factory=UserFactory)
        ManagerSeeder.__init__(self, UserManager())
        self.role_manager = RoleManager()

    def _create_admin_user(self):
        test_user_email = os.getenv('TEST_USER_EMAIL')

        if self.manager.find_by_email(email=test_user_email) is None:
            role = self.role_manager.find_by_name('admin')

            UserFactory.create(
                **{
                    'email': test_user_email,
                    'password': User.ensure_password(os.getenv('TEST_USER_PASSWORD')),
                    'deleted_at': None,
                    'active': True,
                    'created_by': None,
                    'roles': [role],
                }
            )

    @seed_actions
    def seed(self, rows: int = 20):
        self._create_admin_user()
        self.factory.create_batch(rows)
