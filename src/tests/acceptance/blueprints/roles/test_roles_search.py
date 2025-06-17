import pytest

from app.database.factories.role_factory import RoleFactory

from ._base_roles_test import _TestBaseRoleEndpoints


# pylint: disable=attribute-defined-outside-init
class TestSearchRoleEndpoint(_TestBaseRoleEndpoints):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
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

        response = self.client.post(self.endpoint, json=payload, headers=self.build_headers(), exp_code=200)
        json_response = response.get_json()
        role_data = json_response.get('data')
        records_total = json_response.get('records_total')
        records_filtered = json_response.get('records_filtered')

        assert isinstance(role_data, list)
        assert records_total > 0
        assert 0 < records_filtered <= records_total
        assert role_data[0]['name'].find(self.role.name) != -1

    @pytest.mark.parametrize(
        'user_email_attr, expected_status',
        [
            ('admin_user', 200),
            ('team_leader_user', 403),
            ('worker_user', 403),
        ],
    )
    def test_check_user_roles_in_search_roles_endpoint(self, user_email_attr, expected_status):
        user_email = getattr(self, user_email_attr).email
        self.client.post(
            self.endpoint, json={}, headers=self.build_headers(user_email=user_email), exp_code=expected_status
        )
