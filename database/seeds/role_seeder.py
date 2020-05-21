from app.models.role import Role as RoleModel
from database import seed_actions
from database.factories import Factory

class RoleSeeder():
    name = 'RoleSeeder'

    @seed_actions
    def __init__(self, rows: int = 10):
        admin_role = RoleModel.get_or_none(slug='admin')

        if admin_role is None:
            params = {
                'name': 'admin',
                'description': 'administrator',
                'slug': 'admin',
                'deleted_at': None,
            }
            Factory('Role').save(params)

        Factory('Role', rows).save()