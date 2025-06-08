from app.database.factories.user_factory import UserFactory
from app.extensions import db
from app.models import Role
from app.models.role import TEAM_LEADER_ROLE

from ._base_integration_test import _BaseUserEndpointsTest


class GetUserEndpointTest(_BaseUserEndpointsTest):
    def setUp(self):
        super().setUp()
        self.role = db.session.query(Role).filter_by(name=TEAM_LEADER_ROLE).first()
        self.user = UserFactory(active=True, deleted_at=None, roles=[self.role])
        self.endpoint = f'{self.base_path}/{self.user.id}'

    def test_get_user_endpoint(self):
        response = self.client.get(self.endpoint, json={}, headers=self.build_headers())
        json_response = response.get_json()
        json_data = json_response.get('data')

        self.assertEqual(self.user.id, json_data.get('id'))
        self.assertEqual(self.user.name, json_data.get('name'))
        self.assertEqual(self.user.last_name, json_data.get('last_name'))
        self.assertEqual(self.user.birth_date.strftime('%Y-%m-%d'), json_data.get('birth_date'))
        self.assertEqual(self.user.created_at.strftime('%Y-%m-%d %H:%M:%S'), json_data.get('created_at'))
        self.assertEqual(self.user.updated_at.strftime('%Y-%m-%d %H:%M:%S'), json_data.get('updated_at'))
        self.assertEqual(self.user.deleted_at, json_data.get('deleted_at'))

        role_data = json_data.get('roles')[0]
        role = self.role
        self.assertEqual(role.name, role_data.get('name'))
        self.assertEqual(role.label, role_data.get('label'))

    def test_check_user_roles_in_get_user_endpoint(self):
        test_cases = [
            (self.admin_user.email, 200),
            (self.team_leader_user.email, 200),
            (self.worker_user.email, 403),
        ]

        for user_email, response_status in test_cases:
            self.client.get(
                self.endpoint, json={}, headers=self.build_headers(user_email=user_email), exp_code=response_status
            )
