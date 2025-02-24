import unicodedata
import uuid

import factory

from app.database.factories.base_factory import BaseFactory
from app.models import Role
from app.models.role import ADMIN_ROLE, ROLE_NAME_DELIMITER, TEAM_LEADER_ROLE, WORKER_ROLE


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
    name = ADMIN_ROLE
    description = 'Administrator'
    label = 'Admin'


class TeamLeaderRoleFactory(RoleFactory):
    name = TEAM_LEADER_ROLE
    description = 'Team Leader'
    label = 'Team Leader'


class WorkerRoleFactory(RoleFactory):
    name = WORKER_ROLE
    description = 'Worker'
    label = 'Worker'


ROLE_DEFINITIONS = [
    {'name': AdminRoleFactory.name, 'description': AdminRoleFactory.description, 'label': AdminRoleFactory.label},
    {
        'name': TeamLeaderRoleFactory.name,
        'description': TeamLeaderRoleFactory.description,
        'label': TeamLeaderRoleFactory.label,
    },
    {'name': WorkerRoleFactory.name, 'description': WorkerRoleFactory.description, 'label': WorkerRoleFactory.label},
]
