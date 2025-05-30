from app.database.factories.role_factory import RoleFactory

from ._base_integration_test import _BaseRoleEndpointsTest


class SearchRoleEndpointTest(_BaseRoleEndpointsTest):
    def setUp(self):
        super().setUp()
        self.role = RoleFactory(deleted_at=None)
        self.endpoint = f'{self.base_path}/search'

    def test_search_roles_endpoint(self):
        payload = {
            'search': [
                {
                    'field_name': 'name',
                    'field_operator': 'eq',
                    'field_value': self.role.name,
                },
            ],
            'order': [
                {
                    'field_name': 'name',
                    'sorting': 'desc',
                },
            ],
        }

        response = self.client.post(self.endpoint, json=payload, headers=self.build_headers())
        json_response = response.get_json()

        role_data = json_response.get('data')
        records_total = json_response.get('records_total')
        records_filtered = json_response.get('records_filtered')

        self.assertEqual(200, response.status_code)
        self.assertTrue(isinstance(role_data, list))
        self.assertGreater(records_total, 0)
        self.assertTrue(0 < records_filtered <= records_total)
        self.assertTrue(role_data[0]['name'].find(self.role.name) != -1)

    def test_check_user_roles_in_search_roles_endpoint(self):
        test_cases = [
            (self.admin_user.email, 200),
            (self.team_leader_user.email, 403),
            (self.worker_user.email, 403),
        ]

        for user_email, response_status in test_cases:
            with self.subTest(user_email=user_email):
                response = self.client.post(self.endpoint, json={}, headers=self.build_headers(user_email=user_email))
                json_response = response.get_json()

                self.assertEqual(response_status, response.status_code, json_response)
