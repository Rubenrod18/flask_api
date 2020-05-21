from flask import Request, Response

class middleware():
    '''
    Simple WSGI middleware for checking if the request content type is valid.
    '''

    def __init__(self, app):
        self.app = app
        self.accept_content_types = {
            'application/json',
            'application/x-www-form-urlencoded',
        }

    def __call__(self, environ, start_response):
        request = Request(environ)
        content_type = request.content_type

        if content_type in self.accept_content_types:
            return self.app(environ, start_response)

        response = Response('{"message": "Content type no valid"}', mimetype='aplication/json',
                            status=400)
        return response(environ, start_response)
