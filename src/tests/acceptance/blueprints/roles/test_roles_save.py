import pytest

from app.database.factories.role_factory import RoleFactory

from ._base_roles_test import _TestBaseRoleEndpoints


class TestSaveRoleEndpointTest(_TestBaseRoleEndpoints):
    def test_save_role_endpoint(self):
        ignore_fields = {'id', 'created_at', 'updated_at', 'deleted_at', 'name'}
        payload = RoleFactory.build_dict(exclude=ignore_fields)

        response = self.client.post(self.base_path, json=payload, headers=self.build_headers())
        json_response = response.get_json()
        json_data = json_response.get('data')

        assert payload.get('label') == json_data.get('label')
        assert payload.get('label').lower().replace(' ', '-'), json_data.get('name')
        assert json_data.get('created_at')
        assert json_data.get('updated_at'), json_data.get('created_at')
        assert json_data.get('deleted_at') is None

    @pytest.mark.parametrize(
        'user_email_attr, expected_status',
        [
            ('admin_user', 422),
            ('team_leader_user', 403),
            ('worker_user', 403),
        ],
    )
    def test_check_user_roles_in_save_role_endpoint(self, user_email_attr, expected_status):
        user_email = getattr(self, user_email_attr).email
        self.client.post(
            f'{self.base_path}',
            json={},
            headers=self.build_headers(user_email=user_email),
            exp_code=expected_status,
        )
