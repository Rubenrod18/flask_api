import functools
import re

from flask import current_app, request
from flask_security.passwordless import login_token_status

from app.utils import TOKEN_REGEX


def token_required(fnc):
    @functools.wraps(fnc)
    def decorator(*args, **kwargs):
        key = current_app.config.get('SECURITY_TOKEN_AUTHENTICATION_HEADER')
        token = request.headers.get(key, '')

        match_data = re.match(TOKEN_REGEX, token)

        if not token or not match_data:
            return {
                'message': 'Token is missing',
            }, 400

        expired, invalid, user = login_token_status(match_data[1])

        if not expired and not invalid and user:
            if user.active:
                return fnc(*args, **kwargs)
            else:
                return {
                    'message': 'User not authorized',
                }, 403
        else:
            return {
                       'message': 'Token invalid',
                   }, 401

    return decorator
