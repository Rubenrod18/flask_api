from http import HTTPStatus

from flask import render_template, request
from flask_restx import Api


class CustomApi(Api):
    def render_doc(self):
        """Override this method to customize the Swagger UI page"""
        if self._doc_view:
            return self._doc_view()
        elif not self._doc:
            self.abort(HTTPStatus.NOT_FOUND)

        scheme = request.headers.get('X-Forwarded-Proto') or 'http'
        host = request.host
        return render_template('swagger/index.html', url=f'{scheme}://{host}')
