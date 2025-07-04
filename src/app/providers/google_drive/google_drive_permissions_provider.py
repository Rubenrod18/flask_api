from google.oauth2 import service_account

from app.decorators.handle_gdrive_errors import handle_gdrive_errors
from app.providers.google_drive._google_drive_base_provider import _GoogleDriveBaseProvider
from app.utils.constants import GoogleDriveRoles, GoogleDriveUserTypes


# pylint: disable=no-member
class GoogleDrivePermissionsProvider(_GoogleDriveBaseProvider):
    def __init__(
        self,
        credentials: service_account.Credentials = None,
        service=None,
        service_account_path: str | None = None,
        enable_google_drive: bool = True,
    ):
        super().__init__(credentials, service, service_account_path, enable_google_drive)
        self.service = self.service.permissions() if self.service else None

    @handle_gdrive_errors()
    def apply_public_read_access_permission(
        self,
        item_id: str,
        permission: dict = None,
        send_notification_email: bool = False,
        fields: str = None,
    ) -> dict:
        fields = fields or 'id'

        # WARNING:
        #   This default permission grants **public read access** to the file (ANYONE with the link can view it).
        #   Intended **only for development/testing**.
        #   Do NOT use this default in production environments for security reasons.
        permission = permission or {
            'type': GoogleDriveUserTypes.ANYONE.value,
            'role': GoogleDriveRoles.READER.value,
        }

        return self.service.create(
            fileId=item_id, body=permission, fields=fields, sendNotificationEmail=send_notification_email
        ).execute()
