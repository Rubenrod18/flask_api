"""Module for managing exceptions.

References
----------
flask-restx: https://flask-restx.readthedocs.io/en/latest/errors.html

"""

import traceback

from flask import current_app, Flask
from marshmallow import ValidationError
from werkzeug.exceptions import Forbidden

from app.extensions import security


def init_app(app: Flask) -> None:
    app.errorhandler(ValidationError)(_handle_validation_error_exception)

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


def _handle_validation_error_exception(ex: ValidationError) -> tuple:
    if current_app.debug:
        traceback.print_exc()
    return {'message': ex.messages}, 422


class FileEmptyError(OSError):
    pass
