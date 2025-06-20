from datetime import datetime

import pytest

from app.database.factories.user_factory import UserFactory
from app.extensions import db
from app.models import Role
from app.models.role import TEAM_LEADER_ROLE

from ._base_users_test import _TestBaseUserEndpointsTest


# pylint: disable=attribute-defined-outside-init
class TestDeleteUserEndpoint(_TestBaseUserEndpointsTest):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.role = db.session.query(Role).filter_by(name=TEAM_LEADER_ROLE).first()
        self.user = UserFactory(active=True, deleted_at=None, roles=[self.role])
        self.endpoint = f'{self.base_path}/{self.user.id}'

    def test_delete_user_endpoint(self):
        response = self.client.delete(self.endpoint, json={}, headers=self.build_headers())
        json_response = response.get_json()
        json_data = json_response.get('data')

        assert self.user.id == json_data.get('id')
        parsed_deleted_at = datetime.fromisoformat(json_data.get('deleted_at'))
        assert isinstance(parsed_deleted_at, datetime)

    @pytest.mark.parametrize(
        'user_email_attr, expected_status',
        [
            ('admin_user', 200),
            ('team_leader_user', 200),
            ('worker_user', 403),
        ],
    )
    def test_check_user_roles_in_delete_user_endpoint(self, user_email_attr, expected_status):
        user_email = getattr(self, user_email_attr).email
        self.client.delete(
            self.endpoint, json={}, headers=self.build_headers(user_email=user_email), exp_code=expected_status
        )
