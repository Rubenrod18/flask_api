from flask import current_app
from google.oauth2 import service_account
from googleapiclient.discovery import build


class _GoogleDriveBaseProvider:
    def __init__(self, credentials: service_account.Credentials = None):
        self.credentials = credentials or service_account.Credentials.from_service_account_file(
            filename=f'{current_app.config.get("ROOT_DIRECTORY")}/service_account.json',
            scopes=['https://www.googleapis.com/auth/drive'],
        )
        self.service = build('drive', 'v3', credentials=self.credentials)
