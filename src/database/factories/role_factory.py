import unicodedata
import uuid

import factory

from app.models import Role
from app.models.role import ROLE_NAME_DELIMITER
from database.factories.base_factory import BaseFactory


class RoleFactory(BaseFactory):
    class Meta:
        model = Role

    name = factory.Sequence(lambda n: f'role_name_{uuid.uuid4().hex}')
    description = factory.Faker('sentence')

    @factory.lazy_attribute
    def label(self):
        clean_name = unicodedata.normalize('NFKD', self.name).encode('ascii', 'ignore').decode('utf8')
        return clean_name.capitalize().replace(ROLE_NAME_DELIMITER, ' ')


class AdminRoleFactory(RoleFactory):
    name = 'admin'
    description = 'Administrator'
    label = 'Admin'


class TeamLeaderRoleFactory(RoleFactory):
    name = 'team_leader'
    description = 'Team Leader'
    label = 'Team Leader'


class WorkerRoleFactory(RoleFactory):
    name = 'worker'
    description = 'Worker'
    label = 'Worker'
