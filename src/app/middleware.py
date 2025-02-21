"""WSGI middleware for validating requests content type."""

import typing as t

from flask import Flask, Request, Response


class ContentTypeValidator:
    """Handles content type validation for API requests."""

    def __init__(self, allowed_types: t.Optional[t.Set[str]] = None):
        self.allowed_types = allowed_types or set()

    @staticmethod
    def parse(content_type: t.Optional[str]) -> str:
        return content_type.split(';')[0] if content_type and ';' in content_type else content_type or ''

    def is_valid(self, content_type: str, accept_mimetypes: bool) -> bool:
        return content_type in self.allowed_types or accept_mimetypes


class Middleware:
    """WSGI middleware for checking if the request has a valid content type."""

    def __init__(self, app: Flask, validator: t.Optional[ContentTypeValidator] = None):
        self.app = app.wsgi_app
        allowed_types = app.config.get('ALLOWED_CONTENT_TYPES', set())
        self.validator = validator or ContentTypeValidator(allowed_types)

    def __call__(self, environ, start_response):
        """Intercept the request, validate content type, and forward or reject it."""
        request = Request(environ)

        if request.path.startswith('/api'):
            content_type = self.validator.parse(request.content_type)
            accept_mimetypes = request.accept_mimetypes.accept_json  # Swagger support

            if content_type in self.validator.allowed_types or accept_mimetypes:
                return self.app(environ, start_response)

            if not self.validator.is_valid(content_type, accept_mimetypes):
                response = Response(
                    response='{"message": "Invalid Content-Type"}',
                    mimetype='application/json',
                    status=400,
                )
                return response(environ, start_response)

        return self.app(environ, start_response)
