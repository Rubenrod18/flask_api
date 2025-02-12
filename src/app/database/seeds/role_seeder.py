from app.extensions import db
from app.models.role import Role as RoleModel
from app.database import seed_actions
from app.database.factories.role_factory import RoleFactory


class Seeder:
    name = 'RoleSeeder'
    priority = 0

    @staticmethod
    def _create_admin_role() -> None:
        admin_role = db.session.query(RoleModel).filter(RoleModel.name == 'admin').first()

        if admin_role is None:
            params = {
                'name': 'admin',
                'description': 'Administrator',
                'label': 'Admin',
                'deleted_at': None,
            }
            RoleFactory.create(**params)

    @staticmethod
    def _create_team_leader() -> None:
        team_leader_role = db.session.query(RoleModel).filter(RoleModel.name == 'team_leader').first()

        if team_leader_role is None:
            params = {
                'name': 'team_leader',
                'description': 'Team leader',
                'label': 'Team leader',
                'deleted_at': None,
            }
            RoleFactory.create(**params)

    @staticmethod
    def _create_worker_role() -> None:
        worker_role = db.session.query(RoleModel).filter(RoleModel.name == 'worker').first()

        if worker_role is None:
            params = {
                'name': 'worker',
                'description': 'Worker',
                'label': 'Worker',
                'deleted_at': None,
            }
            RoleFactory.create(**params)

    @seed_actions
    def __init__(self):
        self._create_admin_role()
        self._create_team_leader()
        self._create_worker_role()
