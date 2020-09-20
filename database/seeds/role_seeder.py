from app.models.role import Role as RoleModel
from database import seed_actions
from database.factories import Factory


class RoleSeeder:
    name = 'RoleSeeder'

    @staticmethod
    def _create_admin_role() -> None:
        admin_role = RoleModel.get_or_none(name='admin')

        if admin_role is None:
            params = {
                'name': 'admin',
                'description': 'Administrator',
                'label': 'Admin',
                'deleted_at': None,
            }
            Factory('Role').save(params)

    @staticmethod
    def _create_team_leader() -> None:
        team_leader_role = RoleModel.get_or_none(name='team_leader')

        if team_leader_role is None:
            params = {
                'name': 'team_leader',
                'description': 'Team leader',
                'label': 'Team leader',
                'deleted_at': None,
            }
            Factory('Role').save(params)

    @staticmethod
    def _create_worker_role() -> None:
        worker_role = RoleModel.get_or_none(name='worker')

        if worker_role is None:
            params = {
                'name': 'worker',
                'description': 'Worker',
                'label': 'Worker',
                'deleted_at': None,
            }
            Factory('Role').save(params)

    @seed_actions
    def __init__(self):
        self._create_admin_role()
        self._create_team_leader()
        self._create_worker_role()
