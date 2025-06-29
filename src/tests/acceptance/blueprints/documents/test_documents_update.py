from datetime import datetime, timedelta, UTC
from urllib.parse import urlparse

import pytest
from flask import current_app

from app.database.factories.document_factory import LocalDocumentFactory
from app.file_storages import LocalStorage
from app.models.document import StorageType

from ._base_documents_test import _TestBaseDocumentEndpoints


# pylint: disable=attribute-defined-outside-init
class TestUpdateDocumentEndpoint(_TestBaseDocumentEndpoints):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.document = LocalDocumentFactory(
            deleted_at=None,
            created_at=datetime.now(UTC) - timedelta(days=1),
        )
        self.endpoint = f'{self.base_path}/{self.document.id}'
        self.local_storage = LocalStorage()

    def test_update_document_endpoint(self):
        pdf_filename = 'example.pdf'
        pdf_file = f'{current_app.config.get("MOCKUP_DIRECTORY")}/{pdf_filename}'
        data = {'document': open(pdf_file, 'rb')}

        response = self.client.put(
            self.endpoint,
            headers=self.build_headers(extra_headers={'Content-Type': 'multipart/form-data'}),
            data=data,
        )
        json_response = response.get_json()
        json_data = json_response.get('data')
        parse_url = urlparse(json_data.get('url'))

        assert isinstance(json_data.get('created_by').get('id'), int)
        assert pdf_filename == json_data.get('name')
        assert self.document.mime_type == json_data.get('mime_type')
        assert self.local_storage.get_filesize(pdf_file) == json_data.get('size')
        assert str(StorageType.LOCAL) == json_data.get('storage_type')
        assert parse_url.scheme and parse_url.netloc
        assert self.document.created_at.strftime('%Y-%m-%d %H:%M:%S') == json_data.get('created_at')
        assert json_data.get('updated_at') >= json_data.get('created_at')
        assert json_data.get('deleted_at') is None

    @pytest.mark.parametrize(
        'user_email_attr, expected_status',
        [
            ('admin_user', 422),
            ('team_leader_user', 422),
            ('worker_user', 422),
        ],
    )
    def test_check_user_roles_in_update_document_endpoint(self, user_email_attr, expected_status):
        user_email = getattr(self, user_email_attr).email
        self.client.put(
            self.endpoint, json={}, headers=self.build_headers(user_email=user_email), exp_code=expected_status
        )
