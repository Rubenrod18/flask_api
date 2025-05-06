"""Module for testing users blueprint."""

import os

from app.database.factories.role_factory import RoleFactory, TeamLeaderRoleFactory
from app.database.factories.user_factory import UserFactory
from app.extensions import db
from tests.base.base_api_test import TestBaseApi


class TestUserEndpoints(TestBaseApi):
    def setUp(self):
        super().setUp()
        self.base_path = f'{self.base_path}/users'
        self.role = TeamLeaderRoleFactory()
        self.user = UserFactory(active=True, deleted_at=None, roles=[self.role])
        # NOTE: Refresh the role to avoid any potential detached instance issue
        db.session.refresh(self.role)

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
        data = UserFactory.build_dict(exclude=ignore_fields)
        data['password'] = os.getenv('TEST_USER_PASSWORD')
        data['role_id'] = role.id

        response = self.client.post(f'{self.base_path}', json=data, headers=self.build_headers())
        json_response = response.get_json()
        json_data = json_response.get('data')

        self.assertEqual(201, response.status_code, json_response)
        self.assertEqual(data.get('name'), json_data.get('name'))
        self.assertEqual(data.get('last_name'), json_data.get('last_name'))
        self.assertEqual(data.get('birth_date'), json_data.get('birth_date'))
        self.assertEqual(data.get('genre'), json_data.get('genre'))
        self.assertTrue(json_data.get('created_at'))
        self.assertEqual(json_data.get('updated_at'), json_data.get('created_at'))
        self.assertIsNone(json_data.get('deleted_at'))

        role_data = json_data.get('roles')[0]

        self.assertEqual(role.name, role_data.get('name'))
        self.assertEqual(role.label, role_data.get('label'))

    def test_create_invalid_user_endpoint(self):
        data = {
            'name': 'string',
            'last_name': 'string',
            'email': 'string',
            'genre': 'string',
            'password': 'string',
            'birth_date': 'string',
            'role_id': 1,
        }

        response = self.client.post(f'{self.base_path}', json=data, headers=self.build_headers())
        self.assertEqual(422, response.status_code)

    def test_update_user_endpoint(self):
        ignore_fields = {'id', 'active', 'created_at', 'updated_at', 'deleted_at', 'created_by', 'roles'}
        data = UserFactory.build_dict(exclude=ignore_fields)

        data['password'] = os.getenv('TEST_USER_PASSWORD')
        role = RoleFactory()
        data['role_id'] = role.id

        response = self.client.put(
            f'{self.base_path}/{self.user.id}', json=data, headers=self.build_headers(user_email=self.user.email)
        )
        json_response = response.get_json()
        json_data = json_response.get('data')

        self.assertEqual(200, response.status_code)
        self.assertEqual(self.user.id, json_data.get('id'), json_response)
        self.assertEqual(data.get('name'), json_data.get('name'))
        self.assertEqual(data.get('last_name'), json_data.get('last_name'))
        self.assertEqual(data.get('birth_date'), json_data.get('birth_date'))
        self.assertEqual(data.get('genre'), json_data.get('genre'))
        self.assertTrue(json_data.get('created_at'))
        self.assertGreaterEqual(json_data.get('updated_at'), json_data.get('created_at'))
        self.assertIsNone(json_data.get('deleted_at'))

        role_data = json_data.get('roles')[0]

        self.assertEqual(role.name, role_data.get('name'))
        self.assertEqual(role.label, role_data.get('label'))

    def test_get_user_endpoint(self):
        response = self.client.get(f'{self.base_path}/{self.user.id}', json={}, headers=self.build_headers())
        json_response = response.get_json()
        json_data = json_response.get('data')

        self.assertEqual(200, response.status_code)
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

    def test_delete_user_endpoint(self):
        response = self.client.delete(f'{self.base_path}/{self.user.id}', json={}, headers=self.build_headers())
        json_response = response.get_json()
        json_data = json_response.get('data')

        self.assertEqual(200, response.status_code)
        self.assertEqual(self.user.id, json_data.get('id'))
        self.assertIsNotNone(json_data.get('deleted_at'))
        self.assertGreaterEqual(json_data.get('deleted_at'), json_data.get('updated_at'))

    def test_search_users_endpoint(self):
        json_body = {
            'search': [
                {
                    'field_name': 'name',
                    'field_operator': 'eq',
                    'field_value': self.user.name,
                },
            ],
            'order': [
                {
                    'field_name': 'name',
                    'sorting': 'desc',
                },
            ],
        }

        response = self.client.post(f'{self.base_path}/search', json=json_body, headers=self.build_headers())
        json_response = response.get_json()

        user_data = json_response.get('data')
        records_total = json_response.get('records_total')
        records_filtered = json_response.get('records_filtered')

        self.assertEqual(200, response.status_code)
        self.assertTrue(isinstance(user_data, list))
        self.assertGreater(records_total, 0)
        self.assertTrue(0 < records_filtered <= records_total)
        self.assertTrue(user_data[0]['name'].find(self.user.name) != -1)

    def test_export_word_endpoint(self):
        auth_headers = self.build_headers()
        json = {}
        test_cases = [
            (f'{self.base_path}/word', auth_headers, json),
            (f'{self.base_path}/word?to_pdf=1', auth_headers, json),
            (f'{self.base_path}/word?to_pdf=0', auth_headers, json),
        ]

        for uri, auth_headers, payload in test_cases:
            with self.subTest(msg=uri):
                response = self.client.post(uri, json=payload, headers=auth_headers)
                json_response = response.get_json()

                self.assertEqual(202, response.status_code)
                self.assertTrue(json_response.get('task'))
                self.assertTrue(json_response.get('url'))

    def test_export_excel_endpoint(self):
        response = self.client.post(f'{self.base_path}/xlsx', json={}, headers=self.build_headers())
        json_response = response.get_json()

        self.assertEqual(202, response.status_code)
        self.assertTrue(json_response.get('task'))
        self.assertTrue(json_response.get('url'))

    def test_export_excel_and_word_endpoint(self):
        response = self.client.post(f'{self.base_path}/word_and_xlsx', json={}, headers=self.build_headers())

        self.assertEqual(202, response.status_code)
        self.assertTrue(isinstance(response.get_json(), dict))
