import os
from random import choice

from sqlalchemy import func

from app.database.factories.user_factory import UserFactory
from app.database.seeds import seed_actions
from app.database.seeds.base_seeder import FactorySeeder, ManagerSeeder
from app.extensions import db
from app.managers import RoleManager, UserManager
from app.models import Role, User
from app.models.role import ADMIN_ROLE, ROLES


class Seeder(FactorySeeder, ManagerSeeder):
    def __init__(self):
        FactorySeeder.__init__(self, name='UserSeeder', priority=1, factory=UserFactory)
        ManagerSeeder.__init__(self, UserManager())
        self.role_manager = RoleManager()
        self._default_rows = 20

    def _create_admin_user(self):
        test_user_email = os.getenv('TEST_USER_EMAIL')

        if self.manager.find_by_email(email=test_user_email) is None:
            role = self.role_manager.find_by_name(ADMIN_ROLE)

            self.factory.create(
                **{
                    'email': test_user_email,
                    'password': User.ensure_password(os.getenv('TEST_USER_PASSWORD')),
                    'deleted_at': None,
                    'active': True,
                    'created_by': None,
                    'roles': [role],
                }
            )

    @staticmethod
    def _random_user() -> User | None:
        return (
            db.session.query(User)
            .join(User.roles)
            .filter(Role.name == ADMIN_ROLE, User.deleted_at.is_(None))
            .order_by(func.random())  # pylint: disable=not-callable
            .limit(1)
            .one_or_none()
        )

    @seed_actions
    def seed(self, rows: int = None) -> None:
        rows = rows or self._default_rows
        self._create_admin_user()
        roles = {role.name: role for role in self.role_manager.get()['query']}

        for _ in range(rows):
            user_role = roles.get(choice(list(ROLES)))
            created_by = self._random_user()
            self.factory.create(roles=[user_role], created_by_user=created_by)
