from datetime import datetime, timedelta, UTC
from urllib.parse import urlparse

from app.database.factories.document_factory import DocumentFactory

from ._base_documents_test import _BaseDocumentEndpointsTest


class GetDocumentEndpointTest(_BaseDocumentEndpointsTest):
    def setUp(self):
        super().setUp()
        self.document = DocumentFactory(
            deleted_at=None,
            created_at=datetime.now(UTC) - timedelta(days=1),
        )
        self.endpoint = f'{self.base_path}/{self.document.id}'

    def test_get_document_data_endpoint(self):
        response = self.client.get(self.endpoint, json={}, headers=self.build_headers())
        json_data = response.get_json()
        parse_url = urlparse(json_data.get('url'))

        self.assertEqual(self.document.created_by, json_data.get('created_by').get('id'))
        self.assertEqual(self.document.name, json_data.get('name'))
        self.assertEqual(self.document.mime_type, json_data.get('mime_type'))
        self.assertEqual(self.document.size, json_data.get('size'))
        self.assertTrue(parse_url.scheme and parse_url.netloc)
        self.assertEqual(self.document.created_at.strftime('%Y-%m-%d %H:%M:%S'), json_data.get('created_at'))
        self.assertEqual(self.document.updated_at.strftime('%Y-%m-%d %H:%M:%S'), json_data.get('updated_at'))
        self.assertEqual(self.document.deleted_at, json_data.get('deleted_at'))

    def test_check_user_roles_in_get_document_endpoint(self):
        test_cases = [
            (self.admin_user.email, 200),
            (self.team_leader_user.email, 200),
            (self.worker_user.email, 200),
        ]

        for user_email, response_status in test_cases:
            self.client.get(
                self.endpoint, json={}, headers=self.build_headers(user_email=user_email), exp_code=response_status
            )

    def test_get_document_file_content_endpoint(self):
        test_cases = ['as_attachment=1', 'as_attachment=0', '']

        for test_case in test_cases:
            response = self.client.get(
                f'{self.endpoint}?{test_case}',
                headers=self.build_headers(
                    extra_headers={'Content-Type': 'application/json', 'Accept': 'application/octet-stream'}
                ),
            )

            self.assertTrue(isinstance(response.get_data(), bytes))
