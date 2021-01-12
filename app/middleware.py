"""WSGI middleware for validating requests content type."""
from flask import Request, Response, Flask


class Middleware:
    """WSGI middleware for checking if the request has a valid content type."""

    def __init__(self, app: Flask):
        self.app = app.wsgi_app
        self.content_types = app.config.get('ALLOWED_CONTENT_TYPES')

    @staticmethod
    def parse_content_type(content_type: str) -> str:
        """Parser a request Content-Type.

        Parameters
        ----------
        content_type : str
            Request Content Type.

        Returns
        -------
        str
            Parsed request Content Type.

        References
        ----------
        RFC 1341 - MIME (Multipurpose Internet Mail Extensions):
        https://tools.ietf.org/html/rfc1341

        Examples
        --------
        >>> from app.middleware import Middleware as m
        >>> m.parse_content_type('multipart/form-data; boundary=something')
        multipart/form-data
        >>> m.parse_content_type('text/html; charset=utf-8')
        text/html

        """
        if content_type is None:
            parsed_content_type = ''
        else:
            parsed_content_type = content_type.split(';')[0] \
                if content_type.find(';') else content_type

        return parsed_content_type

    def __call__(self, environ, start_response):
        request = Request(environ)
        is_api_request = (request.path[1:4] == 'api')

        if is_api_request:
            content_type = self.parse_content_type(request.content_type)
            # accept_mimetypes = request.accept_mimetypes.accept_json

            if content_type in self.content_types:
                return self.app(environ, start_response)

            response = Response(response='{"message": "Content type no valid"}',
                                mimetype='application/json',
                                status=400)
            return response(environ, start_response)
        return self.app(environ, start_response)
