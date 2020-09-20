from flask import Request, Response, Flask


class Middleware:
    """Simple WSGI middleware for checking if the request has a valid content type."""

    def __init__(self, app: Flask):
        self.app = app.wsgi_app
        self.content_types = app.config.get('ALLOWED_CONTENT_TYPES')
        self.accept = ('application/json')

    @staticmethod
    def _parse_content_type(request_content_type: any) -> str:
        """
            Content-Type := type "/" subtype *[";" parameter]
            https://tools.ietf.org/html/rfc1341
        """
        parsed_content_type = ''

        if isinstance(request_content_type, str):
            parsed_content_type = request_content_type.split(';')[0] \
                if request_content_type.find(';') else request_content_type

        return parsed_content_type

    def __call__(self, environ, start_response):
        request = Request(environ)
        is_api_request = (request.path[1:4] == 'api')

        if is_api_request:
            content_type = self._parse_content_type(request.content_type)
            accept_mimetypes = request.accept_mimetypes.accept_json

            if content_type in self.content_types or accept_mimetypes:
                return self.app(environ, start_response)

            response = Response('{"message": "Content type no valid"}',
                                mimetype='aplication/json',
                                status=400)
            return response(environ, start_response)
        return self.app(environ, start_response)
