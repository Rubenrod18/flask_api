import os
import random
from datetime import timedelta
from random import randint

import factory
from sqlalchemy import func

from app.database.factories.base_factory import BaseFactory, faker
from app.database.factories.role_factory import AdminRoleFactory, RoleFactory, TeamLeaderRoleFactory, WorkerRoleFactory
from app.extensions import db
from app.managers import UserManager
from app.models import Role, User
from app.models.role import ADMIN_ROLE
from app.models.user import Genre
from app.serializers import UserSerializer

UserList = list[User]
_user_manager = UserManager()


class UserFactory(BaseFactory):
    class Meta:
        model = User

    fs_uniquifier = factory.Faker('uuid4')
    name = factory.Faker('name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    genre = factory.Iterator(Genre.to_list())
    birth_date = faker.date_time_between(start_date='-30y', end_date='-5y')
    active = factory.Faker('boolean')

    @classmethod
    def build_dict(cls, exclude: set = None, **kwargs):
        data = super().build_dict(exclude=exclude, **kwargs)
        user_serializer = UserSerializer()
        return user_serializer.dump(data)

    @factory.lazy_attribute
    def password(self):
        return User.ensure_password(os.getenv('TEST_USER_PASSWORD'))

    @factory.lazy_attribute
    def created_by(self):
        user = (
            db.session.query(User)
            .join(User.roles)
            .filter(User.deleted_at.is_(None), Role.name == ADMIN_ROLE)
            .order_by(func.random())  # pylint: disable=not-callable
            .limit(1)
            .one_or_none()
        )
        return None if user is None else user.id

    @factory.lazy_attribute
    def roles(self):
        return [RoleFactory()]

    @factory.lazy_attribute
    def created_at(self):
        return faker.date_time_between(start_date='-3y', end_date='now')

    @factory.lazy_attribute
    def deleted_at(self):
        return random.choice([faker.date_time_between(start_date='-1y', end_date='now'), None])

    @factory.lazy_attribute
    def updated_at(self):
        if self.deleted_at:
            updated_at = self.deleted_at
        else:
            updated_at = self.created_at + timedelta(days=randint(1, 30), minutes=randint(0, 60))
        return updated_at


class AdminUserFactory(UserFactory):
    @factory.lazy_attribute
    def roles(self):
        return [AdminRoleFactory()]


class TeamLeaderUserFactory(UserFactory):
    @factory.lazy_attribute
    def roles(self):
        return [TeamLeaderRoleFactory()]


class WorkerUserFactory(UserFactory):
    @factory.lazy_attribute
    def roles(self):
        return [WorkerRoleFactory()]
