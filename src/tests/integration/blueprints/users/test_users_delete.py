from app.database.factories.user_factory import UserFactory
from app.extensions import db
from app.models import Role
from app.models.role import TEAM_LEADER_ROLE

from ._base_integration_test import _BaseUsersIntegrationTest


class DeleteUsersIntegrationTest(_BaseUsersIntegrationTest):
    def setUp(self):
        super().setUp()
        self.role = db.session.query(Role).filter_by(name=TEAM_LEADER_ROLE).first()
        self.user = UserFactory(active=True, deleted_at=None, roles=[self.role])
        self.endpoint = f'{self.base_path}/{self.user.id}'

    def test_delete_user_endpoint(self):
        response = self.client.delete(self.endpoint, json={}, headers=self.build_headers())
        json_response = response.get_json()
        json_data = json_response.get('data')

        self.assertEqual(200, response.status_code)
        self.assertEqual(self.user.id, json_data.get('id'))
        self.assertIsNotNone(json_data.get('deleted_at'))
        self.assertGreaterEqual(json_data.get('deleted_at'), json_data.get('updated_at'))

    def test_check_user_roles_in_delete_user_endpoint(self):
        test_cases = [
            (self.admin_user.email, 200),
            (self.team_leader_user.email, 404),
            (self.worker_user.email, 403),
        ]

        for user_email, response_status in test_cases:
            with self.subTest(user_email=user_email):
                response = self.client.delete(self.endpoint, json={}, headers=self.build_headers(user_email=user_email))
                json_response = response.get_json()

                self.assertEqual(response_status, response.status_code, json_response)
