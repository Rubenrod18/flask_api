from google.oauth2 import service_account
from googleapiclient.discovery import build


class _GoogleDriveBaseProvider:
    def __init__(
        self,
        credentials: service_account.Credentials = None,
        service=None,
        service_account_path: str | None = None,
        enable_google_drive: bool = True,
    ):
        if not enable_google_drive:
            self.credentials = None
            self.service = service
            return

        if not service_account_path:
            raise ValueError('`service_account_path` must be provided if credentials are not supplied.')

        self.credentials = credentials or service_account.Credentials.from_service_account_file(
            filename=service_account_path,
            scopes=['https://www.googleapis.com/auth/drive'],
        )
        self.service = service or build('drive', 'v3', credentials=self.credentials)
