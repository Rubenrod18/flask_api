from unittest.mock import Mock

import pytest
from googleapiclient.errors import HttpError

from app.decorators.handle_gdrive_errors import handle_gdrive_errors
from app.exceptions import GoogleDriveError, GoogleDriveNotFoundError, GoogleDrivePermissionError


def mock_http_error(status_code, message='Error'):
    resp = Mock()
    resp.status = status_code
    return HttpError(resp=resp, content=bytes(message, 'utf-8'))


class TestHandleGDriveErrors:
    def test_permission_error_raises_google_drive_permission_error(self):
        @handle_gdrive_errors()
        def fake_method():
            raise mock_http_error(403)

        with pytest.raises(GoogleDrivePermissionError) as exc_info:
            fake_method()

        assert 'Access denied' in str(exc_info.value)

    def test_not_found_error_raises_google_drive_not_found_error(self):
        @handle_gdrive_errors()
        def fake_method():
            raise mock_http_error(404)

        with pytest.raises(GoogleDriveNotFoundError) as exc_info:
            fake_method()

        assert 'not found' in str(exc_info.value)

    def test_other_http_error_raises_generic_error(self):
        @handle_gdrive_errors()
        def fake_method():
            raise mock_http_error(500, 'Internal error')

        with pytest.raises(GoogleDriveError) as exc_info:
            fake_method()

        assert 'Unexpected error' in str(exc_info.value)

    def test_successful_function_returns_value(self):
        @handle_gdrive_errors()
        def fake_method():
            return 'OK'

        assert fake_method() == 'OK'
