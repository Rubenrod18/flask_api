from datetime import datetime, timedelta
from random import randint

from app.models.role import Role as RoleModel
from database import fake


class _RoleFactory():
    def _fill(self, data: dict = None) -> dict:
        if data is None:
            data = {}

        current_date = datetime.utcnow()

        created_at = current_date - timedelta(days=randint(1, 100), minutes=randint(0, 60))
        updated_at = created_at
        deleted_at = None

        if randint(0, 1):
            deleted_at = created_at + timedelta(days=randint(1, 30), minutes=randint(0, 60))
        else:
            updated_at = created_at + timedelta(days=randint(1, 30), minutes=randint(0, 60))

        role_name = data.get('name') if data.get('name') else ' '.join(fake.words(nb=2))
        role_slug = role_name.lower().replace(' ', '-')

        return {
            'name': role_name,
            'description': data.get('description') if data.get('description') else fake.sentence(),
            'slug': role_slug,
            'created_at': created_at,
            'updated_at': updated_at,
            'deleted_at': deleted_at,
        }

    def make(self, data: dict = None) -> RoleModel:
        data = self._fill(data)

        role = RoleModel()
        role.name = data.get('name')
        role.description = data.get('description')
        role.slug = data.get('slug')
        role.created_at = data.get('created_at')
        role.updated_at = data.get('updated_at')
        role.deleted_at = data.get('deleted_at')

        return role

    def create(self, data: dict = None) -> RoleModel:
        kwargs = self._fill(data)

        return RoleModel.create(**kwargs)