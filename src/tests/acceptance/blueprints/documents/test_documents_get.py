import io
from datetime import datetime, timedelta, UTC
from unittest.mock import Mock
from urllib.parse import urlparse

import pytest

from app.services import DocumentService
from app.utils.constants import PDF_MIME_TYPE
from tests.factories.document_factory import GDriveDocumentFactory, LocalDocumentFactory

from ._base_documents_test import _TestBaseDocumentEndpoints


# pylint: disable=attribute-defined-outside-init
class TestGetDocumentEndpoint(_TestBaseDocumentEndpoints):
    def test_get_document_data_endpoint(self):
        document = LocalDocumentFactory(
            deleted_at=None,
            created_at=datetime.now(UTC) - timedelta(days=1),
        )

        response = self.client.get(f'{self.base_path}/{document.id}', json={}, headers=self.build_headers())
        json_data = response.get_json()
        parse_url = urlparse(json_data.get('url'))

        assert document.created_by == json_data.get('created_by').get('id')
        assert document.name == json_data.get('name')
        assert document.mime_type == json_data.get('mime_type')
        assert document.size == json_data.get('size')
        assert str(document.storage_type) == json_data.get('storage_type')
        assert parse_url.scheme and parse_url.netloc
        assert document.created_at.strftime('%Y-%m-%d %H:%M:%S') == json_data.get('created_at')
        assert document.updated_at.strftime('%Y-%m-%d %H:%M:%S') == json_data.get('updated_at')
        assert document.deleted_at == json_data.get('deleted_at')

    @pytest.mark.parametrize(
        'user_email_attr, expected_status',
        [
            ('admin_user', 200),
            ('team_leader_user', 200),
            ('worker_user', 200),
        ],
    )
    def test_check_user_roles_in_get_document_endpoint(self, user_email_attr, expected_status):
        document = LocalDocumentFactory(
            deleted_at=None,
            created_at=datetime.now(UTC) - timedelta(days=1),
        )
        user_email = getattr(self, user_email_attr).email

        self.client.get(
            f'{self.base_path}/{document.id}',
            json={},
            headers=self.build_headers(user_email=user_email),
            exp_code=expected_status,
        )

    @pytest.mark.parametrize(
        'as_attachment',
        ['as_attachment=1', 'as_attachment=0', '', 'storage_type=local'],
    )
    def test_get_local_document_file_content_endpoint(self, as_attachment):
        document = LocalDocumentFactory(
            deleted_at=None,
            created_at=datetime.now(UTC) - timedelta(days=1),
        )

        response = self.client.get(
            f'{self.base_path}/{document.id}?{as_attachment}',
            headers=self.build_headers(
                extra_headers={'Content-Type': 'application/json', 'Accept': 'application/octet-stream'}
            ),
        )

        assert isinstance(response.get_data(), bytes)

    @pytest.mark.parametrize(
        'request_args, send_file_kwargs',
        [
            (
                'storage_type=gdrive&as_attachment=1',
                {
                    'path_or_file': io.BytesIO(b''),
                    'as_attachment': 1,
                    'mimetype': PDF_MIME_TYPE,
                    'download_name': 'document_name_0.pdf',
                },
            ),
            (
                'storage_type=gdrive&as_attachment=0',
                {
                    'path_or_file': io.BytesIO(b''),
                    'as_attachment': 0,
                    'mimetype': PDF_MIME_TYPE,
                    'download_name': 'document_name_1.pdf',
                },
            ),
            (
                'storage_type=gdrive',
                {
                    'path_or_file': io.BytesIO(b''),
                    'as_attachment': 0,
                    'mimetype': PDF_MIME_TYPE,
                    'download_name': 'document_name_2.pdf',
                },
            ),
        ],
    )
    def test_get_gdrive_document_file_content_endpoint(self, app, request_args, send_file_kwargs):
        document = GDriveDocumentFactory(
            deleted_at=None,
            created_at=datetime.now(UTC) - timedelta(days=1),
        )

        mock_document_service = Mock(spec=DocumentService)
        mock_document_service.get_document_content.return_value = send_file_kwargs

        with app.container.document_service.override(mock_document_service):
            response = self.client.get(
                f'{self.base_path}/{document.id}?{request_args}',
                headers=self.build_headers(
                    extra_headers={'Content-Type': 'application/json', 'Accept': 'application/octet-stream'}
                ),
            )

        assert isinstance(response.get_data(), bytes)

    @pytest.mark.parametrize(
        'factory, extra_headers',
        [
            (LocalDocumentFactory, {'Content-Type': 'application/json', 'Accept': 'application/octet-stream'}),
            (GDriveDocumentFactory, {'Content-Type': 'application/json', 'Accept': 'application/octet-stream'}),
            (LocalDocumentFactory, {}),
            (GDriveDocumentFactory, {}),
        ],
        ids=['local_file_stream', 'gdrive_file_stream', 'local_json', 'gdrive_json'],
    )
    def test_get_document_is_deleted(self, factory, extra_headers):
        document = factory(deleted_at=datetime.now(UTC))

        response = self.client.get(
            f'{self.base_path}/{document.id}',
            json={},
            headers=self.build_headers(extra_headers=extra_headers),
            exp_code=404,
        )
        json_response = response.get_json()

        assert json_response == {'message': 'Document not found'}, json_response
