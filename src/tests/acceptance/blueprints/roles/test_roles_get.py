from app.database.factories.role_factory import RoleFactory

from ._base_roles_test import _BaseRoleEndpointsTest


class GetRoleEndpointTest(_BaseRoleEndpointsTest):
    def setUp(self):
        super().setUp()
        self.role = RoleFactory(deleted_at=None)
        self.endpoint = f'{self.base_path}/{self.role.id}'

    def test_get_role_endpoint(self):
        response = self.client.get(self.endpoint, json={}, headers=self.build_headers())
        json_response = response.get_json()
        json_data = json_response.get('data')

        self.assertEqual(self.role.id, json_data.get('id'))
        self.assertEqual(self.role.name, json_data.get('name'))
        self.assertEqual(self.role.name.lower(), json_data.get('name').lower().replace('-', ' '))
        self.assertEqual(self.role.created_at.strftime('%Y-%m-%d %H:%M:%S'), json_data.get('created_at'))
        self.assertEqual(self.role.updated_at.strftime('%Y-%m-%d %H:%M:%S'), json_data.get('updated_at'))
        self.assertEqual(self.role.deleted_at, json_data.get('deleted_at'))

    def test_check_user_roles_in_get_role_endpoint(self):
        test_cases = [
            (self.admin_user.email, 200),
            (self.team_leader_user.email, 403),
            (self.worker_user.email, 403),
        ]

        for user_email, response_status in test_cases:
            self.client.get(
                self.endpoint, json={}, headers=self.build_headers(user_email=user_email), exp_code=response_status
            )
