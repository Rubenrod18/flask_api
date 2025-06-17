import pytest

from app.database.factories.user_factory import UserFactory
from app.extensions import db
from app.models import Role
from app.models.role import TEAM_LEADER_ROLE

from ._base_users_test import _TestBaseUserEndpointsTest


class TestSearchUserEndpoint(_TestBaseUserEndpointsTest):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.role = db.session.query(Role).filter_by(name=TEAM_LEADER_ROLE).first()
        self.user = UserFactory(active=True, deleted_at=None, roles=[self.role])
        self.endpoint = f'{self.base_path}/search'

    def test_search_users_endpoint(self):
        payload = {
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

        response = self.client.post(self.endpoint, json=payload, headers=self.build_headers(), exp_code=200)
        json_response = response.get_json()
        user_data = json_response.get('data')
        records_total = json_response.get('records_total')
        records_filtered = json_response.get('records_filtered')

        assert isinstance(user_data, list)
        assert records_total > 0
        assert 0 < records_filtered <= records_total
        assert user_data[0]['name'].find(self.user.name) != -1

    def test_check_user_roles_in_search_users_endpoint(self):
        test_cases = [
            (self.admin_user.email, 200),
            (self.team_leader_user.email, 200),
            (self.worker_user.email, 403),
        ]

        for user_email, response_status in test_cases:
            self.client.post(
                self.endpoint, json={}, headers=self.build_headers(user_email=user_email), exp_code=response_status
            )
