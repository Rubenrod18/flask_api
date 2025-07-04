from datetime import datetime, timedelta, UTC

import pytest

from app.database.factories.document_factory import LocalDocumentFactory
from tests.acceptance.blueprints.documents._base_documents_test import _TestBaseDocumentEndpoints


# pylint: disable=attribute-defined-outside-init
class TestDeleteDocumentEndpoint(_TestBaseDocumentEndpoints):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.document = LocalDocumentFactory(
            deleted_at=None,
            created_at=datetime.now(UTC) - timedelta(days=1),
        )
        self.endpoint = f'{self.base_path}/{self.document.id}'

    def test_delete_document_endpoint(self):
        response = self.client.delete(self.endpoint, json={}, headers=self.build_headers())
        json_response = response.get_json()
        json_data = json_response.get('data')

        assert self.document.id == json_data.get('id')
        parsed_deleted_at = datetime.fromisoformat(json_data.get('deleted_at'))
        assert isinstance(parsed_deleted_at, datetime)

    @pytest.mark.parametrize(
        'user_email_attr, expected_status',
        [
            ('admin_user', 200),
            ('team_leader_user', 200),
            ('worker_user', 200),
        ],
    )
    def test_check_user_roles_in_delete_document_endpoint(self, user_email_attr, expected_status):
        user_email = getattr(self, user_email_attr).email
        self.client.delete(
            self.endpoint, json={}, headers=self.build_headers(user_email=user_email), exp_code=expected_status
        )
