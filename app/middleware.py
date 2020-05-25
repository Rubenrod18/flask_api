from flask import Request, Response


class middleware():
    '''
    Simple WSGI middleware for checking if the request content type is valid.
    '''

    def __init__(self, app):
        self.app = app
        self.accept_content_types = {
            'application/json',
            'multipart/form-data',
            'application/octet-stream',
        }

    def _parse_content_type(self, request_content_type: any) -> str:
        parsed_content_type = ''

        if isinstance(request_content_type, str):
            parsed_content_type = request_content_type.split(';')[0] if request_content_type.find(
                ';') else request_content_type

        return parsed_content_type

    def __call__(self, environ, start_response):
        request = Request(environ)
        # Content-Type := type "/" subtype *[";" parameter]
        # https://tools.ietf.org/html/rfc1341
        content_type = self._parse_content_type(request.content_type)

        if content_type in self.accept_content_types:
            return self.app(environ, start_response)

        response = Response('{"message": "Content type no valid"}', mimetype='aplication/json',
                            status=400)
        return response(environ, start_response)
