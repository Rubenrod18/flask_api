from datetime import datetime, UTC

import pytest

from app.models.role import ROLE_NAME_DELIMITER
from tests.factories.role_factory import RoleFactory

from ._base_roles_test import _TestBaseRoleEndpoints


# pylint: disable=attribute-defined-outside-init
class TestUpdateRoleEndpoint(_TestBaseRoleEndpoints):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.role = RoleFactory(deleted_at=None)
        self.endpoint = f'{self.base_path}/{self.role.id}'

    def test_update_role_endpoint(self):
        ignore_fields = {'id', 'created_at', 'updated_at', 'deleted_at', 'name'}
        payload = RoleFactory.build_dict(exclude=ignore_fields)

        response = self.client.put(self.endpoint, json=payload, headers=self.build_headers())
        json_response = response.get_json()
        json_data = json_response.get('data')

        assert self.role.id == json_data.get('id')
        assert payload.get('label') == json_data.get('label')
        assert payload.get('label').lower().replace(' ', ROLE_NAME_DELIMITER) == json_data.get('name')
        assert json_data.get('created_at')
        assert json_data.get('updated_at') >= json_data.get('created_at')
        assert json_data.get('deleted_at') is None

    @pytest.mark.parametrize(
        'user_email_attr, expected_status',
        [
            ('admin_user', 422),
            ('team_leader_user', 403),
            ('worker_user', 403),
        ],
    )
    def test_check_user_roles_in_update_role_endpoint(self, user_email_attr, expected_status):
        user_email = getattr(self, user_email_attr).email
        self.client.put(
            self.endpoint, json={}, headers=self.build_headers(user_email=user_email), exp_code=expected_status
        )

    @pytest.mark.parametrize(
        'role_label',
        (
            lambda: RoleFactory(deleted_at=None).label,
            lambda: RoleFactory(deleted_at=datetime.now(UTC)).label,
        ),
        ids=['no_deleted', 'deleted'],
    )
    def test_update_role_already_created(self, role_label):
        payload = {'label': role_label(), 'description': self.faker.sentence()}

        response = self.client.put(self.endpoint, json=payload, headers=self.build_headers(), exp_code=422)
        json_response = response.get_json()

        assert json_response == {'message': {'name': ['Role name already created']}}
