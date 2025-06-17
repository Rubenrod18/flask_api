from urllib.parse import urlparse

import pytest
from flask import current_app

from app.file_storages import LocalStorage
from app.utils.constants import PDF_MIME_TYPE

from ._base_documents_test import _TestBaseDocumentEndpoints


# pylint: disable=attribute-defined-outside-init
class TestSaveDocumentEndpoint(_TestBaseDocumentEndpoints):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.local_storage = LocalStorage()

    def test_save_document_endpoint(self):
        pdf_filename = 'example.pdf'
        pdf_file = f'{current_app.config.get("MOCKUP_DIRECTORY")}/{pdf_filename}'
        payload = {
            'document': open(pdf_file, 'rb'),
        }
        headers = self.build_headers()
        headers['Content-Type'] = 'multipart/form-data'

        response = self.client.post(self.base_path, data=payload, headers=headers)
        json_response = response.get_json()
        json_data = json_response.get('data')
        parse_url = urlparse(json_data.get('url'))

        assert self.admin_user.id == json_data.get('created_by').get('id')
        assert pdf_filename == json_data.get('name')
        assert PDF_MIME_TYPE == json_data.get('mime_type')
        assert self.local_storage.get_filesize(pdf_file) == json_data.get('size')
        assert parse_url.scheme and parse_url.netloc
        assert json_data.get('created_at')
        assert json_data.get('updated_at') == json_data.get('created_at')
        assert json_data.get('deleted_at') is None

    @pytest.mark.parametrize(
        'user_email_attr, expected_status',
        [
            ('admin_user', 422),
            ('team_leader_user', 422),
            ('worker_user', 422),
        ],
    )
    def test_check_user_roles_in_save_document_endpoint(self, user_email_attr, expected_status):
        user_email = getattr(self, user_email_attr).email
        self.client.post(
            self.base_path, json={}, headers=self.build_headers(user_email=user_email), exp_code=expected_status
        )
