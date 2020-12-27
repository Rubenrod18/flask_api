"""Module for managing exceptions.

References
----------
flask-restx: https://flask-restx.readthedocs.io/en/latest/errors.html

"""
import traceback

from flask_restx import Api
from flask import current_app
from marshmallow import ValidationError


def init_app(app) -> None:
    app.errorhandler(ValidationError)(handle_validation_error_exception)


def handle_validation_error_exception(ex):
    if current_app.debug:
        traceback.print_exc()

    delattr(ex, 'data')  # Must to be deleted for returning our custom message.
    return {'message': ex.messages}, 422
