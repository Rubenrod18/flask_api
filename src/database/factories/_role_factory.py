from datetime import UTC, datetime, timedelta
from random import randint

from app.models.role import Role as RoleModel
from app.utils import ignore_keys
from database import fake
from database.factories import serialize_dict


class _RoleFactory:
    @staticmethod
    def _fill(params: dict, exclude: list) -> dict:
        current_date = datetime.now(UTC)

        created_at = current_date - timedelta(days=randint(31, 100),
                                              minutes=randint(0, 60))
        updated_at = created_at
        deleted_at = None

        if randint(0, 1) and 'deleted_at' not in params:
            deleted_at = created_at + timedelta(days=randint(1, 30),
                                                minutes=randint(0, 60))
        else:
            updated_at = created_at + timedelta(days=randint(1, 30),
                                                minutes=randint(0, 60))

        role_name = params.get('name') or ' '.join(fake.words(nb=2))
        role_label = role_name.capitalize().replace('-', ' ')

        data = {
            'name': role_name,
            'description': params.get('description') or fake.sentence(),
            'label': role_label,
            'created_at': created_at,
            'updated_at': updated_at,
            'deleted_at': deleted_at,
        }

        return ignore_keys(data, exclude)

    def make(self, params: dict, to_dict: bool, exclude: list) -> RoleModel:
        data = self._fill(params, exclude)

        if to_dict:
            role = serialize_dict(data)
        else:
            model_data = {
                item: data.get(item)
                for item in RoleModel.get_fields(exclude)
            }
            role = RoleModel(**model_data)

        return role

    def create(self, params: dict) -> RoleModel:
        data = self._fill(params, exclude=[])
        return RoleModel(**data)

    def bulk_create(self, total: int, params: dict) -> bool:
        data = []

        for item in range(total):
            data.append(self.make(params, to_dict=False, exclude=[]))

        RoleModel.bulk_create(data)
        return True
