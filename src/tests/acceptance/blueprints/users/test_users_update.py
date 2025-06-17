import os

import pytest

from app.database.factories.role_factory import RoleFactory
from app.database.factories.user_factory import UserFactory
from app.extensions import db
from app.models import Role
from app.models.role import TEAM_LEADER_ROLE

from ._base_users_test import _TestBaseUserEndpointsTest


# pylint: disable=attribute-defined-outside-init
class TestUpdateUserEndpoint(_TestBaseUserEndpointsTest):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.role = db.session.query(Role).filter_by(name=TEAM_LEADER_ROLE).first()
        self.user = UserFactory(active=True, deleted_at=None, roles=[self.role])
        self.endpoint = f'{self.base_path}/{self.user.id}'

    def test_update_user_endpoint(self):
        ignore_fields = {'id', 'active', 'created_at', 'updated_at', 'deleted_at', 'created_by', 'roles'}
        payload = UserFactory.build_dict(exclude=ignore_fields)
        payload['password'] = os.getenv('TEST_USER_PASSWORD')
        role = RoleFactory(deleted_at=None)
        payload['role_id'] = role.id

        response = self.client.put(self.endpoint, json=payload, headers=self.build_headers(user_email=self.user.email))
        json_response = response.get_json()
        json_data = json_response.get('data')
        role_data = json_data.get('roles')[0]

        assert self.user.id == json_data.get('id'), json_response
        assert payload.get('name') == json_data.get('name')
        assert payload.get('last_name') == json_data.get('last_name')
        assert payload.get('birth_date') == json_data.get('birth_date')
        assert payload.get('genre') == json_data.get('genre')
        assert json_data.get('created_at')
        assert json_data.get('updated_at') >= json_data.get('created_at')
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
    def test_check_user_roles_in_update_user_endpoint(self, user_email_attr, expected_status):
        user_email = getattr(self, user_email_attr).email
        self.client.put(
            self.endpoint, json={}, headers=self.build_headers(user_email=user_email), exp_code=expected_status
        )
