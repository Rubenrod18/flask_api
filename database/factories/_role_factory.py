from datetime import datetime, timedelta
from random import randint

from app.models.role import Role as RoleModel
from app.utils import ignore_keys
from database import fake


class _RoleFactory():
    def _fill(self, params: dict, exclude: list) -> dict:
        current_date = datetime.utcnow()

        created_at = current_date - timedelta(days=randint(31, 100), minutes=randint(0, 60))
        updated_at = created_at
        deleted_at = None

        if randint(0, 1):
            deleted_at = created_at + timedelta(days=randint(1, 30), minutes=randint(0, 60))
        else:
            updated_at = created_at + timedelta(days=randint(1, 30), minutes=randint(0, 60))

        role_name = params.get('name') or ' '.join(fake.words(nb=2))
        role_slug = role_name.lower().replace(' ', '-')

        data = {
            'name': role_name,
            'description': params.get('description') or fake.sentence(),
            'slug': role_slug,
            'created_at': created_at,
            'updated_at': updated_at,
            'deleted_at': deleted_at,
        }

        return ignore_keys(data, exclude)

    def make(self, params: dict, to_dict: bool, exclude: list) -> RoleModel:
        data = self._fill(params, exclude)

        if to_dict:
            role = data
        else:
            role = RoleModel()
            role.name = data.get('name')
            role.description = data.get('description')
            role.slug = data.get('slug')
            role.created_at = data.get('created_at')
            role.updated_at = data.get('updated_at')
            role.deleted_at = data.get('deleted_at')

        return role

    def create(self, params: dict) -> RoleModel:
        exclude = []

        data = self._fill(params, exclude)

        return RoleModel.create(**data)

    def bulk_create(self, total: int, params: dict) -> bool:
        data = []

        for item in range(total):
            data.append(self.make(params, False, []))

        RoleModel.bulk_create(data)

        return True
