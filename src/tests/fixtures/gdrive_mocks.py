# pylint: disable=unused-argument
from unittest import mock
from unittest.mock import MagicMock

import pytest

from app.providers.google_drive import GoogleDriveFilesProvider, GoogleDrivePermissionsProvider


@pytest.fixture
def mock_gdrive_files_provider(app):
    """Returns a mocked GoogleDriveFilesProvider (MagicMock) and its internal permissions mock."""
    with (
        mock.patch('app.providers.google_drive._google_drive_base_provider.build', autospec=True) as mock_build,
        mock.patch(
            target=(
                'app.providers.google_drive._google_drive_base_provider.'
                'service_account.Credentials.from_service_account_file'
            ),
            autospec=True,
        ),
    ):
        mock_files = mock.MagicMock()
        mock_service = mock.MagicMock()
        mock_service.files.return_value = mock_files
        mock_build.return_value = mock_service

        provider = MagicMock(spec=GoogleDriveFilesProvider)
        provider.service = mock_service
        provider.enable_google_drive = False

        return provider, mock_files


@pytest.fixture
def mock_gdrive_permissions_provider(app):
    """Returns a mocked GoogleDrivePermissionsProvider (MagicMock) and its internal permissions mock."""
    with (
        mock.patch('app.providers.google_drive._google_drive_base_provider.build', autospec=True) as mock_build,
        mock.patch(
            target='app.providers.google_drive._google_drive_base_provider.'
            'service_account.Credentials.from_service_account_file',
            autospec=True,
        ),
    ):
        mock_permissions = mock.MagicMock()
        mock_service = mock.MagicMock()
        mock_service.permissions.return_value = mock_permissions
        mock_build.return_value = mock_service

        provider = MagicMock(spec=GoogleDrivePermissionsProvider)
        provider.service = mock_service
        provider.enable_google_drive = False

        return provider, mock_permissions
