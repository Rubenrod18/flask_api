import pytest

from app.database.factories.role_factory import RoleFactory
from tests.acceptance.blueprints.roles._base_roles_test import _TestBaseRoleEndpoints


class TestDeleteRoleEndpoint(_TestBaseRoleEndpoints):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.role = RoleFactory(deleted_at=None)
        self.endpoint = f'{self.base_path}/{self.role.id}'

    def test_delete_role_endpoint(self):
        response = self.client.delete(self.endpoint, json={}, headers=self.build_headers())
        json_response = response.get_json()
        json_data = json_response.get('data')

        assert self.role.id == json_data.get('id')
        assert json_data.get('deleted_at') is not None
        assert json_data.get('deleted_at') >= json_data.get('updated_at')

    @pytest.mark.parametrize(
        'user_email_attr, expected_status',
        [
            ('admin_user', 200),
            ('team_leader_user', 403),
            ('worker_user', 403),
        ],
    )
    def test_check_user_roles_in_delete_role_endpoint(self, user_email_attr, expected_status):
        user_email = getattr(self, user_email_attr).email
        self.client.delete(
            self.endpoint, json={}, headers=self.build_headers(user_email=user_email), exp_code=expected_status
        )
