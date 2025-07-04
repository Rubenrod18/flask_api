import os
from random import choice

from sqlalchemy import func

from app.extensions import db
from app.models import Role, User
from app.models.role import ADMIN_ROLE, ROLES
from app.repositories import RoleRepository, UserRepository
from tests.factories.user_factory import UserFactory
from tests.seeds import seed_actions
from tests.seeds.base_seeder import FactorySeeder, RepositorySeeder


class Seeder(FactorySeeder, RepositorySeeder):
    def __init__(self):
        FactorySeeder.__init__(self, name='UserSeeder', priority=1, factory=UserFactory)
        RepositorySeeder.__init__(self, UserRepository())
        self.role_repository = RoleRepository()
        self._default_rows = 20

    def _create_admin_user(self):
        test_user_email = os.getenv('TEST_USER_EMAIL')

        if self.repository.find_by_email(email=test_user_email) is None:
            role = self.role_repository.find_by_name(ADMIN_ROLE)

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
        roles = {role.name: role for role in self.role_repository.get()['query']}

        for _ in range(rows):
            user_role = roles.get(choice(list(ROLES)))
            created_by = self._random_user()
            self.factory.create(roles=[user_role], created_by_user=created_by)
