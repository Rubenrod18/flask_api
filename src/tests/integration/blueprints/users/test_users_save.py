import os

from app.database.factories.role_factory import RoleFactory
from app.database.factories.user_factory import UserFactory

from ._base_integration_test import _BaseUserEndpointsTest


class SaveUserEndpointTest(_BaseUserEndpointsTest):
    def test_create_user_endpoint(self):
        role = RoleFactory()
        ignore_fields = {
            'id',
            'active',
            'created_at',
            'updated_at',
            'deleted_at',
            'created_by',
            'fs_uniquifier',
            'roles',
        }
        payload = UserFactory.build_dict(exclude=ignore_fields)
        payload['password'] = os.getenv('TEST_USER_PASSWORD')
        payload['role_id'] = role.id

        response = self.client.post(self.base_path, json=payload, headers=self.build_headers())
        json_response = response.get_json()
        json_data = json_response.get('data')
        role_data = json_data.get('roles')[0]

        self.assertEqual(payload.get('name'), json_data.get('name'))
        self.assertEqual(payload.get('last_name'), json_data.get('last_name'))
        self.assertEqual(payload.get('birth_date'), json_data.get('birth_date'))
        self.assertEqual(payload.get('genre'), json_data.get('genre'))
        self.assertTrue(json_data.get('created_at'))
        self.assertEqual(json_data.get('updated_at'), json_data.get('created_at'))
        self.assertIsNone(json_data.get('deleted_at'))
        self.assertEqual(role.name, role_data.get('name'))
        self.assertEqual(role.label, role_data.get('label'))

    def test_check_user_roles_in_create_user_endpoint(self):
        test_cases = [
            (self.admin_user.email, 422),
            (self.team_leader_user.email, 422),
            (self.worker_user.email, 403),
        ]

        for user_email, response_status in test_cases:
            with self.subTest(user_email=user_email):
                self.client.post(
                    self.base_path, json={}, headers=self.build_headers(user_email=user_email), exp_code=response_status
                )

    def test_create_invalid_user_endpoint(self):
        payload = {
            'name': 'string',
            'last_name': 'string',
            'email': 'string',
            'genre': 'string',
            'password': 'string',
            'birth_date': 'string',
            'role_id': 1,
        }

        self.client.post(self.base_path, json=payload, headers=self.build_headers(), exp_code=422)
