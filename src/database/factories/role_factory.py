import unicodedata

import factory

from app.models import Role as RoleModel
from app.models.role import ROLE_NAME_DELIMITER
from database.factories.base_factory import BaseFactory


class RoleFactory(BaseFactory):
    class Meta:
        model = RoleModel

    name = factory.Sequence(lambda n: f'role_name_{n}')
    description = factory.Faker('sentence')

    @factory.lazy_attribute
    def label(self):
        clean_name = unicodedata.normalize('NFKD', self.name).encode('ascii', 'ignore').decode('utf8')
        return clean_name.capitalize().replace(ROLE_NAME_DELIMITER, ' ')
