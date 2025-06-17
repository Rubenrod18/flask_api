import pytest

from app.database.factories.user_factory import UserFactory
from app.extensions import db
from app.models import Role
from app.models.role import TEAM_LEADER_ROLE

from ._base_users_test import _TestBaseUserEndpointsTest


class TestGetUserEndpoint(_TestBaseUserEndpointsTest):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.role = db.session.query(Role).filter_by(name=TEAM_LEADER_ROLE).first()
        self.user = UserFactory(active=True, deleted_at=None, roles=[self.role])
        self.endpoint = f'{self.base_path}/{self.user.id}'

    def test_get_user_endpoint(self):
        response = self.client.get(self.endpoint, json={}, headers=self.build_headers())
        json_response = response.get_json()
        json_data = json_response.get('data')

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

    @pytest.mark.parametrize(
        'user_email_attr, expected_status',
        [
            ('admin_user', 200),
            ('team_leader_user', 200),
            ('worker_user', 403),
        ],
    )
    def test_check_user_roles_in_get_user_endpoint(self, user_email_attr, expected_status):
        user_email = getattr(self, user_email_attr).email
        self.client.get(
            self.endpoint, json={}, headers=self.build_headers(user_email=user_email), exp_code=expected_status
        )
