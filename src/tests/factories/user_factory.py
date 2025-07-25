import os
import random

import factory
from sqlalchemy import func

from app.extensions import db
from app.models import Role, User
from app.models.role import ADMIN_ROLE
from app.models.user import Genre
from app.serializers import UserSerializer
from tests.factories.base_factory import BaseFactory
from tests.factories.role_factory import AdminRoleFactory, RoleFactory, TeamLeaderRoleFactory, WorkerRoleFactory


class UserFactory(BaseFactory):
    class Meta:
        model = User

    fs_uniquifier = factory.Faker('uuid4')
    name = factory.Faker('name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    genre = factory.Iterator(Genre.to_list())
    birth_date = factory.Faker('date_time_between', start_date='-30y', end_date='-5y')
    active = factory.Faker('boolean')
    created_at = factory.Faker('date_time_between', start_date='-3y', end_date='now')
    deleted_at = random.choice([factory.Faker('date_time_between', start_date='-1y', end_date='now'), None])

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
    def updated_at(self):
        if self.deleted_at:
            updated_at = self.deleted_at
        else:
            # NOTE: This case always applies on the creation
            updated_at = self.created_at
        return updated_at


class AdminUserFactory(UserFactory):
    name = 'admin_name'
    last_name = 'admin_last_name'

    @factory.lazy_attribute
    def roles(self):
        return [AdminRoleFactory(deleted_at=None)]


class TeamLeaderUserFactory(UserFactory):
    name = 'team_leader_name'
    last_name = 'team_leader_last_name'

    @factory.lazy_attribute
    def roles(self):
        return [TeamLeaderRoleFactory(deleted_at=None)]


class WorkerUserFactory(UserFactory):
    name = 'worker_name'
    last_name = 'worker_last_name'

    @factory.lazy_attribute
    def roles(self):
        return [WorkerRoleFactory(deleted_at=None)]
