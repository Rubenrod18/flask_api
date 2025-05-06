"""Module for testing documents blueprint."""

from datetime import datetime, timedelta, UTC
from urllib.parse import urlparse

from flask import current_app

from app.database.factories.document_factory import DocumentFactory
from app.helpers.file_storage.local_storage import LocalStorage
from tests.base.base_api_test import TestBaseApi


class TestDocumentEndpoints(TestBaseApi):
    def setUp(self):
        super().setUp()
        self.base_path = f'{self.base_path}/documents'
        self.document = DocumentFactory(
            deleted_at=None,
            created_at=datetime.now(UTC) - timedelta(days=1),
        )
        self.local_storage = LocalStorage()

    def test_save_document_endpoint(self):
        pdf_file = f'{current_app.config.get("MOCKUP_DIRECTORY")}/example.pdf'
        data = {
            'document': open(pdf_file, 'rb'),
        }

        headers = self.build_headers()
        headers['Content-Type'] = 'multipart/form-data'

        response = self.client.post(f'{self.base_path}', data=data, headers=headers)
        json_response = response.get_json()
        json_data = json_response.get('data')

        parse_url = urlparse(json_data.get('url'))

        self.assertEqual(201, response.status_code)
        self.assertEqual(self.admin_user.id, json_data.get('created_by').get('id'))
        self.assertEqual(pdf_file, json_data.get('name'))
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
            with self.subTest(user_email=user_email):
                response = self.client.post(
                    f'{self.base_path}', json={}, headers=self.build_headers(user_email=user_email)
                )
                json_response = response.get_json()

                self.assertEqual(response_status, response.status_code, json_response)

    def test_update_document_endpoint(self):
        pdf_file = f'{current_app.config.get("MOCKUP_DIRECTORY")}/example.pdf'
        data = {'document': open(pdf_file, 'rb')}

        response = self.client.put(
            f'{self.base_path}/{self.document.id}',
            headers=self.build_headers(extra_headers={'Content-Type': 'multipart/form-data'}),
            data=data,
        )
        json_response = response.get_json()
        json_data = json_response.get('data')

        parse_url = urlparse(json_data.get('url'))

        self.assertEqual(200, response.status_code)
        self.assertTrue(isinstance(json_data.get('created_by').get('id'), int))
        self.assertEqual(pdf_file, json_data.get('name'))
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
            with self.subTest(user_email=user_email):
                response = self.client.put(
                    f'{self.base_path}/{self.document.id}', json={}, headers=self.build_headers(user_email=user_email)
                )
                json_response = response.get_json()

                self.assertEqual(response_status, response.status_code, json_response)

    def test_get_document_data_endpoint(self):
        response = self.client.get(f'{self.base_path}/{self.document.id}', json={}, headers=self.build_headers())
        json_data = response.get_json()

        parse_url = urlparse(json_data.get('url'))

        self.assertEqual(200, response.status_code)
        self.assertEqual(self.document.created_by, json_data.get('created_by').get('id'))
        self.assertEqual(self.document.name, json_data.get('name'))
        self.assertEqual(self.document.mime_type, json_data.get('mime_type'))
        self.assertEqual(self.document.size, json_data.get('size'))
        self.assertTrue(parse_url.scheme and parse_url.netloc)
        self.assertEqual(self.document.created_at.strftime('%Y-%m-%d %H:%M:%S'), json_data.get('created_at'))
        self.assertEqual(self.document.updated_at.strftime('%Y-%m-%d %H:%M:%S'), json_data.get('updated_at'))
        self.assertEqual(self.document.deleted_at, json_data.get('deleted_at'))

    def test_check_user_roles_in_get_document_data_endpoint(self):
        test_cases = [
            (self.admin_user.email, 200),
            (self.team_leader_user.email, 200),
            (self.worker_user.email, 200),
        ]

        for user_email, response_status in test_cases:
            with self.subTest(user_email=user_email):
                response = self.client.get(
                    f'{self.base_path}/{self.document.id}', json={}, headers=self.build_headers(user_email=user_email)
                )
                json_response = response.get_json()

                self.assertEqual(response_status, response.status_code, json_response)

    def test_get_document_file_endpoint(self):
        test_cases = ['as_attachment=1', 'as_attachment=0', '']

        for test_case in test_cases:
            with self.subTest(test_case):
                response = self.client.get(
                    f'{self.base_path}/{self.document.id}?{test_case}',
                    headers=self.build_headers(
                        extra_headers={'Content-Type': 'application/json', 'Accept': 'application/octet-stream'}
                    ),
                )

                self.assertEqual(200, response.status_code)
                self.assertTrue(isinstance(response.get_data(), bytes))

    def test_check_user_roles_in_get_document_file_endpoint(self):
        test_cases = [
            (self.admin_user.email, 200),
            (self.team_leader_user.email, 200),
            (self.worker_user.email, 200),
        ]

        for user_email, response_status in test_cases:
            with self.subTest(user_email=user_email):
                response = self.client.get(
                    f'{self.base_path}/{self.document.id}',
                    json={},
                    headers=self.build_headers(
                        user_email=user_email,
                        extra_headers={'Content-Type': 'application/json', 'Accept': 'application/octet-stream'},
                    ),
                )
                json_response = response.get_json()

                self.assertEqual(response_status, response.status_code, json_response)

    def test_delete_document_endpoint(self):
        response = self.client.delete(f'{self.base_path}/{self.document.id}', json={}, headers=self.build_headers())
        json_response = response.get_json()
        json_data = json_response.get('data')

        self.assertEqual(200, response.status_code)
        self.assertEqual(self.document.id, json_data.get('id'))
        self.assertIsNotNone(json_data.get('deleted_at'))
        self.assertGreaterEqual(json_data.get('deleted_at'), json_data.get('updated_at'))

    def test_check_user_roles_in_delete_document_endpoint(self):
        test_cases = [
            (self.admin_user.email, 200),
            (self.team_leader_user.email, 404),
            (self.worker_user.email, 404),
        ]

        for user_email, response_status in test_cases:
            with self.subTest(user_email=user_email):
                response = self.client.delete(
                    f'{self.base_path}/{self.document.id}', json={}, headers=self.build_headers(user_email=user_email)
                )
                json_response = response.get_json()

                self.assertEqual(response_status, response.status_code, json_response)

    def test_search_document_endpoint(self):
        json_body = {
            'search': [
                {
                    'field_name': 'name',
                    'field_operator': 'eq',
                    'field_value': self.document.name,
                },
            ],
            'order': [
                {
                    'field_name': 'name',
                    'sorting': 'desc',
                },
            ],
        }

        response = self.client.post(f'{self.base_path}/search', json=json_body, headers=self.build_headers())
        json_response = response.get_json()

        document_data = json_response.get('data')
        records_total = json_response.get('records_total')
        records_filtered = json_response.get('records_filtered')

        self.assertEqual(200, response.status_code)
        self.assertTrue(isinstance(document_data, list))
        self.assertGreater(records_total, 0)
        self.assertTrue(0 < records_filtered <= records_total)
        self.assertTrue(document_data[0].get('name').find(self.document.name) != -1)

    def test_check_user_roles_in_search_document_endpoint(self):
        test_cases = [
            (self.admin_user.email, 200),
            (self.team_leader_user.email, 200),
            (self.worker_user.email, 200),
        ]

        for user_email, response_status in test_cases:
            with self.subTest(user_email=user_email):
                response = self.client.post(
                    f'{self.base_path}/search', json={}, headers=self.build_headers(user_email=user_email)
                )
                json_response = response.get_json()

                self.assertEqual(response_status, response.status_code, json_response)
