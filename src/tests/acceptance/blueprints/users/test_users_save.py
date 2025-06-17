import os

import pytest

from app.database.factories.role_factory import RoleFactory
from app.database.factories.user_factory import UserFactory

from ._base_users_test import _TestBaseUserEndpointsTest


# pylint: disable=attribute-defined-outside-init
class TestSaveUserEndpoint(_TestBaseUserEndpointsTest):
    def test_create_user_endpoint(self):
        role = RoleFactory(deleted_at=None)
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

        assert payload.get('name') == json_data.get('name')
        assert payload.get('last_name') == json_data.get('last_name')
        assert payload.get('birth_date') == json_data.get('birth_date')
        assert payload.get('genre') == json_data.get('genre')
        assert json_data.get('created_at')
        assert json_data.get('updated_at') == json_data.get('created_at')
        assert json_data.get('deleted_at') is None
        assert role.name == role_data.get('name')
        assert role.label == role_data.get('label')

    @pytest.mark.parametrize(
        'user_email_attr, expected_status',
        [
            ('admin_user', 422),
            ('team_leader_user', 422),
            ('worker_user', 403),
        ],
    )
    def test_check_user_roles_in_create_user_endpoint(self, user_email_attr, expected_status):
        user_email = getattr(self, user_email_attr).email
        self.client.post(
            self.base_path, json={}, headers=self.build_headers(user_email=user_email), exp_code=expected_status
        )

    def test_create_invalid_user_endpoint(self):
        payload = {
            'name': 'string',
            'last_name': 'string',
            'email': 'string',
            'genre': 'string',
            'password': 'string',
            'birth_date': 'string',
            'role_id': self.admin_user.roles[0].id,
        }

        self.client.post(self.base_path, json=payload, headers=self.build_headers(), exp_code=422)
