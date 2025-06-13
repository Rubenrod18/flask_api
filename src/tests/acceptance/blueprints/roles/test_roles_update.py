from app.database.factories.role_factory import RoleFactory

from ._base_roles_test import _BaseRoleEndpointsTest


class UpdateRoleEndpointTest(_BaseRoleEndpointsTest):
    def setUp(self):
        super().setUp()
        self.role = RoleFactory(deleted_at=None)
        self.endpoint = f'{self.base_path}/{self.role.id}'

    def test_update_role_endpoint(self):
        ignore_fields = {'id', 'created_at', 'updated_at', 'deleted_at', 'name'}
        payload = RoleFactory.build_dict(exclude=ignore_fields)

        response = self.client.put(self.endpoint, json=payload, headers=self.build_headers())
        json_response = response.get_json()
        json_data = json_response.get('data')

        self.assertEqual(self.role.id, json_data.get('id'))
        self.assertEqual(payload.get('label'), json_data.get('label'))
        self.assertEqual(payload.get('label').lower().replace(' ', '-'), json_data.get('name'))
        self.assertTrue(json_data.get('created_at'))
        self.assertGreaterEqual(json_data.get('updated_at'), json_data.get('created_at'))
        self.assertIsNone(json_data.get('deleted_at'))

    def test_check_user_roles_in_update_role_endpoint(self):
        test_cases = [
            (self.admin_user.email, 422),
            (self.team_leader_user.email, 403),
            (self.worker_user.email, 403),
        ]

        for user_email, response_status in test_cases:
            self.client.put(
                self.endpoint, json={}, headers=self.build_headers(user_email=user_email), exp_code=response_status
            )
