from datetime import datetime, timedelta, UTC
from urllib.parse import urlparse

from flask import current_app

from app.database.factories.document_factory import DocumentFactory
from app.file_storages import LocalStorage

from ._base_documents_test import _BaseDocumentEndpointsTest


class UpdateDocumentEndpointTest(_BaseDocumentEndpointsTest):
    def setUp(self):
        super().setUp()
        self.document = DocumentFactory(
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

        self.assertTrue(isinstance(json_data.get('created_by').get('id'), int))
        self.assertEqual(pdf_filename, json_data.get('name'))
        self.assertEqual(self.document.mime_type, json_data.get('mime_type'))
        self.assertEqual(self.local_storage.get_filesize(pdf_file), json_data.get('size'))
        self.assertTrue(parse_url.scheme and parse_url.netloc)
        self.assertEqual(self.document.created_at.strftime('%Y-%m-%d %H:%M:%S'), json_data.get('created_at'))
        self.assertTrue(json_data.get('updated_at') > json_data.get('created_at'))
        self.assertTrue(json_data.get('deleted_at') is None)

    def test_check_user_roles_in_update_document_endpoint(self):
        test_cases = [
            (self.admin_user.email, 422),
            (self.team_leader_user.email, 422),
            (self.worker_user.email, 422),
        ]

        for user_email, response_status in test_cases:
            self.client.put(
                self.endpoint, json={}, headers=self.build_headers(user_email=user_email), exp_code=response_status
            )
