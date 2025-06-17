import pytest

from app.database.factories.role_factory import RoleFactory

from ._base_roles_test import _TestBaseRoleEndpoints


class TestGetRoleEndpoint(_TestBaseRoleEndpoints):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.role = RoleFactory(deleted_at=None)
        self.endpoint = f'{self.base_path}/{self.role.id}'

    def test_get_role_endpoint(self):
        response = self.client.get(self.endpoint, json={}, headers=self.build_headers())
        json_response = response.get_json()
        json_data = json_response.get('data')

        assert self.role.id == json_data.get('id')
        assert self.role.name == json_data.get('name')
        assert self.role.name.lower() == json_data.get('name').lower().replace('-', ' ')
        assert self.role.created_at.strftime('%Y-%m-%d %H:%M:%S') == json_data.get('created_at')
        assert self.role.updated_at.strftime('%Y-%m-%d %H:%M:%S') == json_data.get('updated_at')
        assert self.role.deleted_at == json_data.get('deleted_at')

    @pytest.mark.parametrize(
        'user_email_attr, expected_status',
        [
            ('admin_user', 200),
            ('team_leader_user', 403),
            ('worker_user', 403),
        ],
    )
    def test_check_user_roles_in_get_role_endpoint(self, user_email_attr, expected_status):
        user_email = getattr(self, user_email_attr).email
        self.client.get(
            self.endpoint, json={}, headers=self.build_headers(user_email=user_email), exp_code=expected_status
        )
