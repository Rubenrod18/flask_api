"""Module for managing exceptions.

References
----------
flask-restx: https://flask-restx.readthedocs.io/en/latest/errors.html

"""
import traceback

from flask import current_app, Flask
from marshmallow import ValidationError


def init_app(app: Flask) -> None:
    app.errorhandler(ValidationError)(_handle_validation_error_exception)


def _handle_validation_error_exception(ex: ValidationError) -> tuple:
    if current_app.debug:
        traceback.print_exc()
    return {'message': ex.messages}, 422


class FileEmptyError(OSError):
    pass
