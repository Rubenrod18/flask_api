import functools
import re

from flask import current_app, request
from flask_security.passwordless import login_token_status
from werkzeug.exceptions import NotFound, Forbidden, BadRequest, Unauthorized

from app.utils import TOKEN_REGEX


def token_required(fnc):
    @functools.wraps(fnc)
    def decorator(*args, **kwargs):
        key = current_app.config.get('SECURITY_TOKEN_AUTHENTICATION_HEADER')
        token = request.headers.get(key, '')

        match_data = re.match(TOKEN_REGEX, token)

        if not token or not match_data:
            raise Unauthorized('User is not authorized')

        expired, invalid, user = login_token_status(match_data[1])

        if not expired and not invalid and user:
            if user.active:
                return fnc(*args, **kwargs)
            else:
                raise Forbidden('User is not active')
        elif invalid:
            raise BadRequest('Token is invalid')
        else:
            raise BadRequest('Token has expired')

    return decorator
