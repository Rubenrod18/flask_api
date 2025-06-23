import logging
from functools import wraps

from googleapiclient.errors import HttpError

from app.exceptions import GoogleDriveError, GoogleDriveNotFoundError, GoogleDrivePermissionError

logger = logging.getLogger(__name__)


def handle_gdrive_errors():
    gdrive_http_error_map = {
        403: GoogleDrivePermissionError('Access denied or insufficient permissions.'),
        404: GoogleDriveNotFoundError('File or resource not found.'),
    }

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except HttpError as e:
                status = e.resp.status
                logger.error(f'Google API error {status} in {func.__name__}: {e}')

                raise gdrive_http_error_map.get(status, GoogleDriveError(f'Unexpected error: {e}')) from e

        return wrapper

    return decorator
