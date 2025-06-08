from urllib.parse import urlparse

from flask import current_app

from app.file_storages import LocalStorage

from ._base_integration_test import _BaseDocumentEndpointsTest


class GetDocumentEndpointTest(_BaseDocumentEndpointsTest):
    def setUp(self):
        super().setUp()
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

        self.assertEqual(self.admin_user.id, json_data.get('created_by').get('id'))
        self.assertEqual(pdf_filename, json_data.get('name'))
        self.assertEqual('application/pdf', json_data.get('mime_type'))
        self.assertEqual(self.local_storage.get_filesize(pdf_file), json_data.get('size'))
        self.assertTrue(parse_url.scheme and parse_url.netloc)
        self.assertTrue(json_data.get('created_at'))
        self.assertEqual(json_data.get('updated_at'), json_data.get('created_at'))
        self.assertIsNone(json_data.get('deleted_at'))

    def test_check_user_roles_in_save_document_endpoint(self):
        test_cases = [
            (self.admin_user.email, 422),
            (self.team_leader_user.email, 422),
            (self.worker_user.email, 422),
        ]

        for user_email, response_status in test_cases:
            self.client.post(
                self.base_path, json={}, headers=self.build_headers(user_email=user_email), exp_code=response_status
            )
