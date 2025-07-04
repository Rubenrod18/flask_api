"""Module for managing exceptions."""

import logging
import traceback

from flask import current_app, Flask
from marshmallow import ValidationError
from werkzeug.exceptions import Forbidden, HTTPException, InternalServerError

from app.extensions import security

logger = logging.getLogger(__name__)


def init_app(app: Flask) -> None:
    app.errorhandler(ValidationError)(_validation_error_handler)
    app.errorhandler(Exception)(_general_exception_handler)

    @security.unauthz_handler
    def custom_unauthorized_handler(func_name: str, params: list[str]) -> None:  # noqa: F841
        """Custom unauthorized handler.

        Parameters
        ----------
        func_name : str
            The decorator function name (e.g. 'roles_required').
        params : list[str]
            List of what (if any) was passed to the decorator.

        Raises
        ------
        Forbidden
            The auth user doesn't have permission to access this resource.

        """
        raise Forbidden()


def _general_exception_handler(exc: Exception) -> tuple[dict, int]:
    """Custom general error handler."""
    logger.exception(exc)

    if isinstance(exc, HTTPException):
        return {'message': exc.description}, exc.code

    return {'message': InternalServerError.description}, InternalServerError.code


def _validation_error_handler(exc: ValidationError) -> tuple[dict, int]:
    """Custom validation error handler."""
    if current_app.debug:
        traceback.print_exc()

    return {'message': exc.messages}, 422


class FileEmptyError(OSError):
    pass


class GoogleDriveError(Exception):
    """Base exception for Google Drive operations."""


class GoogleDrivePermissionError(GoogleDriveError):
    """Raised when access is denied (403)."""


class GoogleDriveNotFoundError(GoogleDriveError):
    """Raised when the file or folder is not found (404)."""
