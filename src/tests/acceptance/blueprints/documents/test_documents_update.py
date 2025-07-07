from datetime import datetime, timedelta, UTC
from urllib.parse import urlparse

import pytest
from flask import current_app

from app.file_storages import LocalStorage
from app.models.document import StorageTypes
from app.services import DocumentService
from app.utils.constants import MS_EXCEL_MIME_TYPE
from tests.factories.document_factory import GDriveDocumentFactory, LocalDocumentFactory

from ._base_documents_test import _TestBaseDocumentEndpoints


# pylint: disable=attribute-defined-outside-init
class TestUpdateDocumentEndpoint(_TestBaseDocumentEndpoints):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.local_storage = LocalStorage()

    def test_update_document_endpoint(self):
        document = LocalDocumentFactory(
            deleted_at=None,
            created_at=datetime.now(UTC) - timedelta(days=1),
        )

        filename = 'sample.xlsx'
        abs_filepath = f'{current_app.config.get("MOCKUP_DIRECTORY")}/{filename}'
        data = {'document': open(abs_filepath, 'rb')}

        response = self.client.put(
            f'{self.base_path}/{document.id}',
            headers=self.build_headers(extra_headers={'Content-Type': 'multipart/form-data'}),
            data=data,
        )
        json_response = response.get_json()
        json_data = json_response.get('data')
        parse_url = urlparse(json_data.get('url'))

        assert isinstance(json_data.get('created_by').get('id'), int)
        assert filename == json_data.get('name')
        assert document.mime_type == json_data.get('mime_type')
        assert self.local_storage.get_filesize(abs_filepath) == json_data.get('size')
        assert str(StorageTypes.LOCAL) == json_data.get('storage_type')
        assert parse_url.scheme and parse_url.netloc
        assert document.created_at.strftime('%Y-%m-%d %H:%M:%S') == json_data.get('created_at')
        assert json_data.get('updated_at') >= json_data.get('created_at')
        assert json_data.get('deleted_at') is None

    def test_update_document_endpoint_in_google_drive(
        self, mock_gdrive_files_provider, mock_gdrive_permissions_provider
    ):
        document = GDriveDocumentFactory(
            deleted_at=None,
            created_at=datetime.now(UTC) - timedelta(days=1),
        )
        filename = 'sample.xlsx'
        abs_filepath = f'{current_app.config.get("MOCKUP_DIRECTORY")}/{filename}'

        mock_gdrive_files_provider, _ = mock_gdrive_files_provider
        mock_gdrive_files_provider.upload_file_from_stream.return_value = {
            'id': document.storage_id,
            'mimeType': MS_EXCEL_MIME_TYPE,
            'size': 5_425,
            'name': filename,
        }
        mock_gdrive_permissions_provider, _ = mock_gdrive_permissions_provider
        mock_document_service = DocumentService(
            gdrive_files_provider=mock_gdrive_files_provider,
            gdrive_permissions_provider=mock_gdrive_permissions_provider,
        )

        with self.app.container.document_service.override(mock_document_service):
            response = self.client.put(
                f'{self.base_path}/{document.id}?storage_type={StorageTypes.GDRIVE.value}',
                data={'document': open(abs_filepath, 'rb')},
                headers=self.build_headers(extra_headers={'Content-Type': 'multipart/form-data'}),
            )
        json_response = response.get_json()
        json_data = json_response.get('data')
        parse_url = urlparse(json_data.get('url'))

        assert isinstance(json_data.get('created_by').get('id'), int)
        assert filename == json_data.get('name')
        assert document.mime_type == json_data.get('mime_type')
        assert self.local_storage.get_filesize(abs_filepath) == json_data.get('size')
        assert str(StorageTypes.GDRIVE) == json_data.get('storage_type')
        assert parse_url.scheme and parse_url.netloc
        assert document.created_at.strftime('%Y-%m-%d %H:%M:%S') == json_data.get('created_at')
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
        document = LocalDocumentFactory(
            deleted_at=None,
            created_at=datetime.now(UTC) - timedelta(days=1),
        )

        user_email = getattr(self, user_email_attr).email
        self.client.put(
            f'{self.base_path}/{document.id}',
            json={},
            headers=self.build_headers(user_email=user_email),
            exp_code=expected_status,
        )
