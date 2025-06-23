import uuid
from unittest.mock import MagicMock, patch

import pytest
from flask import current_app
from googleapiclient.http import MediaFileUpload

from app.providers.google_drive import GoogleDriveFilesProvider
from app.utils.constants import FOLDER_MIME_TYPE, PDF_MIME_TYPE


@pytest.fixture
def mock_gdrive_files_provider():
    with (
        patch('app.providers.google_drive._google_drive_base_provider.build', autospec=True) as mock_build,
        patch(
            'app.providers.google_drive._google_drive_base_provider.service_account.Credentials.from_service_account_file',
            autospec=True,
        ),
    ):
        mock_files = MagicMock()
        mock_service = MagicMock()
        mock_service.files.return_value = mock_files
        mock_build.return_value = mock_service

        provider = GoogleDriveFilesProvider()
        return provider, mock_files


class TestGoogleDriveFilesProvider:
    @pytest.mark.parametrize(
        'folder_params, folder_params_called, fields',
        [
            (
                {'name': 'custom-folder', 'parent_id': 'parent_id'},
                {'name': 'custom-folder', 'mimeType': FOLDER_MIME_TYPE, 'parents': ['parent_id']},
                None,
            ),
            (
                {'name': 'custom-folder'},
                {'name': 'custom-folder', 'mimeType': FOLDER_MIME_TYPE},
                'id',
            ),
        ],
        ids=['with-parents', 'without-parents'],
    )
    def test_create_folder(self, folder_params, folder_params_called, fields, mock_gdrive_files_provider):
        provider, mock_files = mock_gdrive_files_provider
        folder_data = {'id': uuid.uuid4().hex, 'name': 'custom-folder'}
        mock_create = MagicMock()
        mock_create.execute.return_value = folder_data
        mock_files.create.return_value = mock_create

        result = provider.create_folder(**folder_params, fields=fields)
        fields = fields or 'id, name'

        mock_files.create.assert_called_once_with(body=folder_params_called, fields=fields)
        mock_create.execute.assert_called_once()
        assert result == folder_data

    @pytest.mark.parametrize(
        'file_params, file_params_called, fields',
        [
            (
                {'name': 'example.pdf', 'parent_id': 'parent_id', 'mime_type': PDF_MIME_TYPE},
                {'name': 'example.pdf', 'mimeType': FOLDER_MIME_TYPE, 'parents': ['parent_id']},
                None,
            ),
            (
                {'name': 'example.pdf', 'mime_type': PDF_MIME_TYPE},
                {'name': 'example.pdf', 'mimeType': FOLDER_MIME_TYPE},
                'id',
            ),
        ],
        ids=['with-parents', 'without-parents'],
    )
    def test_create_file(self, file_params, file_params_called, fields, mock_gdrive_files_provider, app):
        provider, mock_files = mock_gdrive_files_provider
        pdf_filename = 'example.pdf'
        file_data = {'id': uuid.uuid4().hex, 'name': pdf_filename}
        mock_create = MagicMock()
        mock_create.execute.return_value = file_data
        mock_files.create.return_value = mock_create

        result = provider.create_file(
            **file_params, path=f'{current_app.config.get("MOCKUP_DIRECTORY")}/{pdf_filename}', fields=fields
        )

        mock_files.create.assert_called_once()
        args, kwargs = mock_files.create.call_args
        assert kwargs['body']['name'] == pdf_filename
        assert kwargs['body'].get('parents') == file_params_called.get('parents')
        assert kwargs['fields'] == fields or 'id, name'
        media_body = kwargs['media_body']
        # NOTE: We can't use `assert_called_once_with` for `media_body` because
        #       `MediaFileUpload` creates a new instance that cannot be directly compared
        #       Instead, we verify that the object is of the correct type and inspect its internal attributes.
        assert isinstance(media_body, MediaFileUpload)
        assert media_body._filename == f'{current_app.config.get("MOCKUP_DIRECTORY")}/{pdf_filename}'
        assert media_body._mimetype == PDF_MIME_TYPE, media_body.mimetype
        mock_create.execute.assert_called_once()
        assert result == file_data

    @pytest.mark.parametrize(
        'file_params, file_params_called',
        [
            (
                5,
                {'pageSize': 5},
            ),
            (
                None,
                {'pageSize': 10},
            ),
        ],
    )
    def test_get_files(self, file_params, file_params_called, mock_gdrive_files_provider):
        provider, mock_files = mock_gdrive_files_provider
        expected_result = [{'id': uuid.uuid4().hex, 'name': 'document.pdf'}]
        mock_get = MagicMock()
        mock_get.execute.return_value = expected_result
        mock_files.list.return_value = mock_get

        result = provider.get_files(file_params)

        mock_files.list.assert_called_once_with(**file_params_called)
        mock_get.execute.assert_called_once()
        assert result == expected_result

    @pytest.mark.parametrize(
        'file_id, fields',
        [
            (
                'file-id',
                None,
            ),
            (
                'file-id',
                'id, name',
            ),
        ],
    )
    def test_get_file_metadata(self, file_id, fields, mock_gdrive_files_provider):
        provider, mock_files = mock_gdrive_files_provider
        expected_result = [{'id': uuid.uuid4().hex, 'name': 'document.pdf'}]
        mock_get = MagicMock()
        mock_get.execute.return_value = expected_result
        mock_files.get.return_value = mock_get

        result = provider.get_file_metadata(file_id, fields)
        fields = fields or 'id, name, mimeType, size, createdTime, modifiedTime, owners, webViewLink'

        mock_files.get.assert_called_once_with(fileId=file_id, fields=fields)
        mock_get.execute.assert_called_once()
        assert result == expected_result

    def test_delete_file(self, mock_gdrive_files_provider):
        provider, mock_files = mock_gdrive_files_provider
        file_id = uuid.uuid4().hex
        expected_result = [{'id': file_id, 'name': 'document.pdf'}]
        mock_delete = MagicMock()
        mock_delete.execute.return_value = expected_result
        mock_files.delete.return_value = mock_delete

        provider.delete_file(file_id)

        mock_files.delete.assert_called_once_with(fileId=file_id)
        mock_delete.execute.assert_called_once()
