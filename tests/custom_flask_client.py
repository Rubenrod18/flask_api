import logging

from flask import Response
from flask.testing import FlaskClient

logger = logging.getLogger(__name__)


class CustomFlaskClient(FlaskClient):
    @staticmethod
    def before_request(*args, **kwargs):
        logger.info(f'args: {args}')
        logger.info(f'kwargs: {kwargs}')

    @staticmethod
    def after_request(response: Response):
        def log_request_data():
            if response.mimetype == 'application/json':
                response_data = response.get_json()
            else:
                response_data = response.data
            logger.info(f'response data: {response_data}')

        logger.info(f'response status code: {response.status_code}')
        logger.info(f'response mime type: {response.mimetype}')
        log_request_data()

    def make_request(self, method: str, *args, **kwargs):
        logger.info('< === START REQUEST === >')
        self.before_request(*args, **kwargs)

        kwargs['method'] = method
        response = self.open(*args, **kwargs)

        self.after_request(response)
        logger.info('< === END REQUEST === >')
        return response

    def get(self, *args, **kwargs):
        """Like open but method is enforced to GET."""
        return self.make_request('GET', *args, **kwargs)

    def post(self, *args, **kwargs):
        """Like open but method is enforced to POST."""
        return self.make_request('POST', *args, **kwargs)

    def put(self, *args, **kwargs):
        """Like open but method is enforced to PUT."""
        return self.make_request('PUT', *args, **kwargs)

    def delete(self, *args, **kwargs):
        """Like open but method is enforced to DELETE."""
        return self.make_request('DELETE', *args, **kwargs)
