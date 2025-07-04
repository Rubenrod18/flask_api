import io
import uuid
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest
from flask import current_app

from app.providers.google_drive import GoogleDriveFilesProvider
from app.utils.constants import FOLDER_MIME_TYPE, PDF_MIME_TYPE


@pytest.fixture
def mock_gdrive_files_provider(app):
    with (
        patch('app.providers.google_drive._google_drive_base_provider.build', autospec=True) as mock_build,
        patch(
            target=(
                'app.providers.google_drive._google_drive_base_provider.'
                'service_account.Credentials.from_service_account_file'
            ),
            autospec=True,
        ),
    ):
        mock_files = MagicMock()
        mock_service = MagicMock()
        mock_service.files.return_value = mock_files
        mock_build.return_value = mock_service

        provider = GoogleDriveFilesProvider()
        return provider, mock_files


# pylint: disable=redefined-outer-name
class TestGoogleDriveFilesProvider:
    @pytest.mark.parametrize(
        'folder_params, payload, fields',
        [
            (
                {'folder_name': 'custom-folder', 'parent_id': 'parent_id'},
                {'name': 'custom-folder', 'mimeType': FOLDER_MIME_TYPE, 'parents': ['parent_id']},
                None,
            ),
            (
                {'folder_name': 'custom-folder'},
                {'name': 'custom-folder', 'mimeType': FOLDER_MIME_TYPE},
                'id',
            ),
        ],
        ids=['with-parents', 'without-parents'],
    )
    def test_create_folder(self, folder_params, payload, fields, mock_gdrive_files_provider):
        provider, mock_files = mock_gdrive_files_provider
        folder_data = {'id': uuid.uuid4().hex, 'name': 'custom-folder'}
        mock_create = MagicMock()
        mock_create.execute.return_value = folder_data
        mock_files.create.return_value = mock_create

        result = provider.create_folder(**folder_params, fields=fields)
        fields = fields or 'id, name'

        mock_files.create.assert_called_once_with(body=payload, fields=fields)
        mock_create.execute.assert_called_once()
        assert result == folder_data

    @pytest.mark.parametrize(
        'folder_params, payload, fields, request_response, method_response',
        [
            (
                {'folder_name': 'custom-folder', 'parent_id': 'parent_id'},
                {
                    'q': (
                        f'mimeType="{FOLDER_MIME_TYPE}" and name="custom-folder" and trashed=false '
                        f'and "parent_id" in parents'
                    ),
                    'fields': 'files(id, name)',
                    'pageSize': 1,
                },
                None,
                {'files': [{'id': 'folder-id', 'name': 'custom-folder'}]},
                {'id': 'folder-id', 'name': 'custom-folder'},
            ),
            (
                {'folder_name': 'custom-folder'},
                {
                    'q': f'mimeType="{FOLDER_MIME_TYPE}" and name="custom-folder" and trashed=false',
                    'fields': 'files(id)',
                    'pageSize': 1,
                },
                'files(id)',
                {'files': []},
                None,
            ),
        ],
        ids=['with-parents', 'without-parents'],
    )
    def test_folder_exists(
        self, folder_params, payload, fields, request_response, method_response, mock_gdrive_files_provider
    ):
        provider, mock_files = mock_gdrive_files_provider
        mock_list = MagicMock()
        mock_list.execute.return_value = request_response
        mock_files.list.return_value = mock_list

        result = provider.folder_exists(**folder_params, fields=fields)

        mock_files.list.assert_called_once_with(**payload)
        mock_list.execute.assert_called_once()
        assert result == method_response

    # pylint: disable=protected-access, disable=unused-argument
    @pytest.mark.parametrize(
        'file_params, payload, fields',
        [
            (
                {'file_name': 'example.pdf', 'parent_id': 'parent_id', 'mime_type': PDF_MIME_TYPE},
                {'body': {'name': 'example.pdf', 'parents': ['parent_id']}, 'media_body': None, 'fields': 'id, name'},
                None,
            ),
            (
                {'file_name': 'example.pdf', 'mime_type': PDF_MIME_TYPE},
                {'body': {'name': 'example.pdf'}, 'media_body': None, 'fields': 'id'},
                'id',
            ),
        ],
        ids=['with-parents', 'without-parents'],
    )
    @mock.patch('app.providers.google_drive.google_drive_files_provider.MediaFileUpload', autospec=True)
    def test_create_file_from_path(
        self, mock_media_file_upload, file_params, payload, fields, mock_gdrive_files_provider, app
    ):
        provider, mock_files = mock_gdrive_files_provider
        pdf_filename = 'example.pdf'
        file_data = {'id': uuid.uuid4().hex, 'name': pdf_filename}

        mock_create = MagicMock()
        mock_create.execute.return_value = file_data
        mock_files.create.return_value = mock_create

        media_file_upload = MagicMock()
        mock_media_file_upload.return_value = media_file_upload
        payload['media_body'] = media_file_upload

        result = provider.create_file_from_path(
            **file_params, file_path=f'{current_app.config.get("MOCKUP_DIRECTORY")}/{pdf_filename}', fields=fields
        )

        mock_media_file_upload.assert_called_once_with(
            f'{current_app.config.get("MOCKUP_DIRECTORY")}/{pdf_filename}', mimetype=PDF_MIME_TYPE
        )
        mock_files.create.assert_called_once_with(**payload)
        mock_create.execute.assert_called_once()
        assert result == file_data

    # pylint: disable=disable=unused-argument
    @pytest.mark.parametrize(
        'file_params, payload, fields',
        [
            (
                {'file_name': 'example.pdf', 'parent_id': 'parent_id', 'mime_type': PDF_MIME_TYPE},
                {'body': {'name': 'example.pdf', 'parents': ['parent_id']}, 'media_body': None, 'fields': 'id, name'},
                None,
            ),
            (
                {'file_name': 'example.pdf', 'mime_type': PDF_MIME_TYPE},
                {'body': {'name': 'example.pdf'}, 'media_body': None, 'fields': 'id'},
                'id',
            ),
        ],
        ids=['with-parents', 'without-parents'],
    )
    @mock.patch('app.providers.google_drive.google_drive_files_provider.MediaIoBaseUpload', autospec=True)
    def test_create_file_from_stream(
        self, mock_media_io_base_upload, file_params, payload, fields, mock_gdrive_files_provider, app
    ):
        provider, mock_files = mock_gdrive_files_provider
        pdf_filename = 'example.pdf'
        file_data = {'id': uuid.uuid4().hex, 'name': pdf_filename}

        mock_create = MagicMock()
        mock_create.execute.return_value = file_data
        mock_files.create.return_value = mock_create

        media_io_upload = MagicMock()
        mock_media_io_base_upload.return_value = media_io_upload
        payload['media_body'] = media_io_upload
        file_stream = io.BytesIO(open(f'{current_app.config.get("MOCKUP_DIRECTORY")}/{pdf_filename}', 'rb').read())

        result = provider.create_file_from_stream(**file_params, file_stream=file_stream, fields=fields)

        mock_media_io_base_upload.assert_called_once_with(file_stream, mimetype=PDF_MIME_TYPE)
        mock_files.create.assert_called_once_with(**payload)
        mock_create.execute.assert_called_once()
        assert result == file_data

    @pytest.mark.parametrize(
        'file_params, payload, fields',
        [
            (
                {
                    'file_id': 'file-id',
                    'file_name': 'example.pdf',
                    'parent_id': 'parent_id',
                    'mime_type': PDF_MIME_TYPE,
                },
                {
                    'fileId': 'file-id',
                    'body': {'name': 'example.pdf', 'parents': ['parent_id']},
                    'media_body': None,
                    'fields': 'id, name, mimeType',
                },
                None,
            ),
            (
                {'file_id': 'file-id', 'file_name': 'example.pdf', 'mime_type': PDF_MIME_TYPE},
                {'fileId': 'file-id', 'body': {'name': 'example.pdf'}, 'media_body': None, 'fields': 'id'},
                'id',
            ),
        ],
        ids=['with-parents', 'without-parents'],
    )
    @mock.patch('app.providers.google_drive.google_drive_files_provider.MediaFileUpload', autospec=True)
    def test_upload_file_from_path(
        self, mock_media_file_upload, file_params, payload, fields, mock_gdrive_files_provider, app
    ):
        provider, mock_files = mock_gdrive_files_provider
        pdf_filename = 'example.pdf'
        file_data = {'id': uuid.uuid4().hex, 'name': pdf_filename}

        mock_update = MagicMock()
        mock_update.execute.return_value = file_data
        mock_files.update.return_value = mock_update

        media_file_upload = MagicMock()
        mock_media_file_upload.return_value = media_file_upload
        payload['media_body'] = media_file_upload

        result = provider.upload_file_from_path(
            **file_params, file_path=f'{current_app.config.get("MOCKUP_DIRECTORY")}/{pdf_filename}', fields=fields
        )

        mock_media_file_upload.assert_called_once_with(
            f'{current_app.config.get("MOCKUP_DIRECTORY")}/{pdf_filename}', mimetype=PDF_MIME_TYPE
        )
        mock_files.update.assert_called_once_with(**payload)
        mock_update.execute.assert_called_once()
        assert result == file_data

    @pytest.mark.parametrize(
        'file_params, payload, fields',
        [
            (
                {
                    'file_id': 'file-id',
                    'file_name': 'example.pdf',
                    'mime_type': PDF_MIME_TYPE,
                },
                {
                    'fileId': 'file-id',
                    'body': {'name': 'example.pdf'},
                    'media_body': None,
                    'fields': 'id, name, mimeType',
                },
                None,
            ),
            (
                {'file_id': 'file-id', 'file_name': 'example.pdf', 'mime_type': PDF_MIME_TYPE},
                {'fileId': 'file-id', 'body': {'name': 'example.pdf'}, 'media_body': None, 'fields': 'id'},
                'id',
            ),
        ],
        ids=['default-fields', 'specific-fields'],
    )
    @mock.patch('app.providers.google_drive.google_drive_files_provider.MediaIoBaseUpload', autospec=True)
    def test_upload_file_from_stream(
        self, mock_media_io_base_upload, file_params, payload, fields, mock_gdrive_files_provider, app
    ):
        provider, mock_files = mock_gdrive_files_provider
        pdf_filename = 'example.pdf'
        file_data = {'id': uuid.uuid4().hex, 'name': pdf_filename}

        mock_update = MagicMock()
        mock_update.execute.return_value = file_data
        mock_files.update.return_value = mock_update

        media_io_upload = MagicMock()
        mock_media_io_base_upload.return_value = media_io_upload
        payload['media_body'] = media_io_upload
        file_stream = io.BytesIO(open(f'{current_app.config.get("MOCKUP_DIRECTORY")}/{pdf_filename}', 'rb').read())

        result = provider.upload_file_from_stream(**file_params, file_stream=file_stream, fields=fields)

        mock_media_io_base_upload.assert_called_once_with(file_stream, mimetype=PDF_MIME_TYPE)
        mock_files.update.assert_called_once_with(**payload)
        mock_update.execute.assert_called_once()
        assert result == file_data

    @pytest.mark.parametrize(
        'file_params, payload',
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
    def test_get_files(self, file_params, payload, mock_gdrive_files_provider):
        provider, mock_files = mock_gdrive_files_provider
        expected_result = [{'id': uuid.uuid4().hex, 'name': 'document.pdf'}]
        mock_get = MagicMock()
        mock_get.execute.return_value = expected_result
        mock_files.list.return_value = mock_get

        result = provider.get_files(file_params)

        mock_files.list.assert_called_once_with(**payload)
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

    @mock.patch('app.providers.google_drive.google_drive_files_provider.MediaIoBaseDownload', autospec=True)
    def test_download_file_content(self, mock_media_io_base_download, mock_gdrive_files_provider):
        provider, mock_files = mock_gdrive_files_provider
        mock_files.get_media.return_value = MagicMock()
        mock_downloader_instance = MagicMock()
        mock_downloader_instance.next_chunk.side_effect = [(mock.Mock(progress=mock.Mock(return_value=1.0)), True)]
        mock_media_io_base_download.return_value = mock_downloader_instance
        file_id = uuid.uuid4().hex

        result = provider.download_file_content(file_id)

        mock_files.get_media.assert_called_once_with(fileId=file_id)
        mock_media_io_base_download.assert_called_once()
        assert isinstance(result, io.BytesIO)
        assert result.tell() == 0  # NOTE: The .tell() method on a file-like object (such as io.BytesIO) returns
        #       the current position of the file pointer. Ensure seek(0) was called.
