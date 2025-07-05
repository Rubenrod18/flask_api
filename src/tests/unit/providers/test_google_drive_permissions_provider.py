import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.providers.google_drive import GoogleDrivePermissionsProvider
from app.utils.constants import GoogleDriveRoles, GoogleDriveUserTypes


@pytest.fixture
def stub_gdrive_permissions_provider():  # pylint: disable=unused-argument
    """Returns a real GoogleDrivePermissionsProvider instance with a mocked service."""
    with (
        patch('app.providers.google_drive._google_drive_base_provider.build', autospec=True) as mock_build,
        patch(
            target='app.providers.google_drive._google_drive_base_provider.'
            'service_account.Credentials.from_service_account_file',
            autospec=True,
        ),
    ):
        mock_permissions = MagicMock()
        mock_service = MagicMock()
        mock_service.permissions.return_value = mock_permissions
        mock_build.return_value = mock_service

        provider = GoogleDrivePermissionsProvider(service=mock_service, enable_google_drive=False)

        return provider, mock_permissions


# pylint: disable=redefined-outer-name
class TestGoogleDrivePermissionsProvider:
    @pytest.mark.parametrize(
        'item_params, payload, fields',
        [
            (
                {'item_id': 'item-id', 'permission': None, 'send_notification_email': False},
                {
                    'fileId': 'item-id',
                    'body': {
                        'type': GoogleDriveUserTypes.ANYONE.value,
                        'role': GoogleDriveRoles.READER.value,
                    },
                    'sendNotificationEmail': False,
                },
                'id',
            ),
            (
                {
                    'item_id': 'item-id',
                    'permission': {
                        'type': GoogleDriveUserTypes.USER.value,
                        'role': GoogleDriveRoles.WRITER.value,
                    },
                    'send_notification_email': True,
                },
                {
                    'fileId': 'item-id',
                    'body': {
                        'type': GoogleDriveUserTypes.USER.value,
                        'role': GoogleDriveRoles.WRITER.value,
                    },
                    'sendNotificationEmail': True,
                },
                'id, name',
            ),
        ],
    )
    def test_apply_public_read_access_permission(self, item_params, payload, fields, stub_gdrive_permissions_provider):
        provider, mock_permissions = stub_gdrive_permissions_provider
        folder_data = {'id': uuid.uuid4().hex, 'name': 'custom-folder'}
        mock_create = MagicMock()
        mock_create.execute.return_value = folder_data
        mock_permissions.create.return_value = mock_create

        result = provider.apply_public_read_access_permission(**item_params, fields=fields)
        fields = fields or 'id'

        mock_permissions.create.assert_called_once_with(**payload, fields=fields)
        mock_create.execute.assert_called_once()
        assert result == folder_data
