"""Module for testing users blueprint."""
import os

from app.extensions import db
from database.factories.role_factory import RoleFactory
from database.factories.user_factory import UserFactory
from tests.base.base_api_test import TestBaseApi


class TestUserEndpoints(TestBaseApi):
    def setUp(self):
        super(TestUserEndpoints, self).setUp()
        self.base_path = f'{self.base_path}/users'
        self.role = RoleFactory()
        self.user = UserFactory(active=True, deleted_at=None, roles=[self.role])
        # Refresh the role to avoid any potential detached instance issue
        db.session.refresh(self.role)

    def test_create_user_endpoint(self):
        role = RoleFactory()

        ignore_fields = {'id', 'active', 'created_at', 'updated_at', 'deleted_at', 'created_by', 'fs_uniquifier', 'roles'}
        data = UserFactory.build_dict(exclude=ignore_fields)
        data['password'] = os.getenv('TEST_USER_PASSWORD')
        data['role_id'] = role.id

        response = self.client.post(f'{self.base_path}', json=data, headers=self.build_headers())
        json_response = response.get_json()
        json_data = json_response.get('data')
    
        assert 201 == response.status_code
        assert data.get('name') == json_data.get('name')
        assert data.get('last_name') == json_data.get('last_name')
        assert data.get('birth_date') == json_data.get('birth_date')
        assert data.get('genre') == json_data.get('genre')
        assert json_data.get('created_at')
        assert json_data.get('updated_at') == json_data.get('created_at')
        assert json_data.get('deleted_at') is None
    
        role_data = json_data.get('roles')[0]
    
        assert role.name == role_data.get('name')
        assert role.label == role_data.get('label')

    def test_create_invalid_user_endpoint(self):
        data = {
          'name': 'string',
          'last_name': 'string',
          'email': 'string',
          'genre': 'string',
          'password': 'string',
          'birth_date': 'string',
          'role_id': 1
        }
    
        response = self.client.post(f'{self.base_path}', json=data, headers=self.build_headers())
        assert 422 == response.status_code
    
    def test_update_user_endpoint(self):
        ignore_fields = {'id', 'active', 'created_at', 'updated_at', 'deleted_at',
                         'created_by', 'roles'}
        data = UserFactory.build_dict(exclude=ignore_fields)
    
        data['password'] = os.getenv('TEST_USER_PASSWORD')
        role = RoleFactory()
        data['role_id'] = role.id
    
        response = self.client.put(f'{self.base_path}/{self.user.id}', json=data, headers=self.build_headers())
        json_response = response.get_json()
        json_data = json_response.get('data')
    
        assert 200 == response.status_code
        assert self.user.id == json_data.get('id')
        assert data.get('name') == json_data.get('name')
        assert data.get('last_name') == json_data.get('last_name')
        assert data.get('birth_date') == json_data.get('birth_date')
        assert data.get('genre') == json_data.get('genre')
        assert json_data.get('created_at')
        assert json_data.get('updated_at') >= json_data.get('created_at')
        assert json_data.get('deleted_at') is None
    
        role_data = json_data.get('roles')[0]
    
        assert role.name == role_data.get('name')
        assert role.label == role_data.get('label')
    
    def test_get_user_endpoint(self):
        response = self.client.get(f'{self.base_path}/{self.user.id}', json={}, headers=self.build_headers())
        json_response = response.get_json()
        json_data = json_response.get('data')
    
        assert 200 == response.status_code
        assert self.user.id == json_data.get('id')
        assert self.user.name == json_data.get('name')
        assert self.user.last_name == json_data.get('last_name')
        assert self.user.birth_date.strftime('%Y-%m-%d') == json_data.get('birth_date')
        assert self.user.created_at.strftime('%Y-%m-%d %H:%M:%S') == json_data.get('created_at')
        assert self.user.updated_at.strftime('%Y-%m-%d %H:%M:%S') == json_data.get('updated_at')
        assert self.user.deleted_at == json_data.get('deleted_at')
    
        role_data = json_data.get('roles')[0]
        role = self.role
        assert role.name == role_data.get('name')
        assert role.label == role_data.get('label')
    
    def test_delete_user_endpoint(self):
        response = self.client.delete(f'{self.base_path}/{self.user.id}', json={}, headers=self.build_headers())
        json_response = response.get_json()
        json_data = json_response.get('data')
    
        assert 200 == response.status_code
        assert self.user.id == json_data.get('id')
        assert json_data.get('deleted_at') is not None
        assert json_data.get('deleted_at') >= json_data.get('updated_at')
    
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
    
        assert 200 == response.status_code
        assert isinstance(user_data, list)
        assert records_total > 0
        assert 0 < records_filtered <= records_total
        assert user_data[0]['name'].find(self.user.name) != -1

    # TODO: pending to refactor the arquitecture
    def xtest_export_word_endpoint(self):
        def _request(uri: str, headers: str, json: dict) -> None:
            response = self.client.post(uri, json=json, headers=headers)
            json_response = response.get_json()
    
            assert 202 == response.status_code
            assert json_response.get('task')
            assert json_response.get('url')
    
        json = {
            'search': [],
            'order': [
                {
                    'field_name': 'name',
                    'sorting': 'desc',
                },
            ],
        }
    
        _request(f'{self.base_path}/word', self.build_headers(), json)
        _request(f'{self.base_path}/word?to_pdf=1', self.build_headers(), json)
        _request(f'{self.base_path}/word?to_pdf=0', self.build_headers(), json)

    # TODO: pending to refactor the arquitecture
    def xtest_export_excel_endpoint(self):
        response = self.client.post(f'{self.base_path}/xlsx', json={}, headers=self.build_headers())
        json_response = response.get_json()
    
        assert 202 == response.status_code
        assert json_response.get('task')
        assert json_response.get('url')

    # TODO: pending to refactor the arquitecture
    def xtest_export_excel_and_word_endpoint(self):
        response = self.client.post(f'{self.base_path}/word_and_xlsx', json={},
                                    headers=self.build_headers())
    
        assert 202 == response.status_code
        assert isinstance(response.get_json(), dict)
