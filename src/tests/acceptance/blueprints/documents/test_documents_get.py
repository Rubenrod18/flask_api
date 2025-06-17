from datetime import datetime, timedelta, UTC
from urllib.parse import urlparse

import pytest

from app.database.factories.document_factory import DocumentFactory

from ._base_documents_test import _TestBaseDocumentEndpoints


# pylint: disable=attribute-defined-outside-init
class TestGetDocumentEndpoint(_TestBaseDocumentEndpoints):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.document = DocumentFactory(
            deleted_at=None,
            created_at=datetime.now(UTC) - timedelta(days=1),
        )
        self.endpoint = f'{self.base_path}/{self.document.id}'

    def test_get_document_data_endpoint(self):
        response = self.client.get(self.endpoint, json={}, headers=self.build_headers())
        json_data = response.get_json()
        parse_url = urlparse(json_data.get('url'))

        assert self.document.created_by == json_data.get('created_by').get('id')
        assert self.document.name == json_data.get('name')
        assert self.document.mime_type == json_data.get('mime_type')
        assert self.document.size == json_data.get('size')
        assert parse_url.scheme and parse_url.netloc
        assert self.document.created_at.strftime('%Y-%m-%d %H:%M:%S') == json_data.get('created_at')
        assert self.document.updated_at.strftime('%Y-%m-%d %H:%M:%S') == json_data.get('updated_at')
        assert self.document.deleted_at == json_data.get('deleted_at')

    @pytest.mark.parametrize(
        'user_email_attr, expected_status',
        [
            ('admin_user', 200),
            ('team_leader_user', 200),
            ('worker_user', 200),
        ],
    )
    def test_check_user_roles_in_get_document_endpoint(self, user_email_attr, expected_status):
        user_email = getattr(self, user_email_attr).email
        self.client.get(
            self.endpoint, json={}, headers=self.build_headers(user_email=user_email), exp_code=expected_status
        )

    @pytest.mark.parametrize(
        'as_attachment',
        [
            'as_attachment=1',
            'as_attachment=0',
            '',
        ],
    )
    def test_get_document_file_content_endpoint(self, as_attachment):
        response = self.client.get(
            f'{self.endpoint}?{as_attachment}',
            headers=self.build_headers(
                extra_headers={'Content-Type': 'application/json', 'Accept': 'application/octet-stream'}
            ),
        )

        assert isinstance(response.get_data(), bytes)
