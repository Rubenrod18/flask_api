from app.models.role import Role as RoleModel
from database.factories import Factory
from database.seeds import seed_actions

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
            }
            Factory('Role').save(params)

        Factory('Role', rows).save()