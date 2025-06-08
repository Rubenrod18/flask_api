"""Main module runs the application.

The module runs the application on differents
configurations ( dev, prod, testing, etc ), run commands, etc.

"""

import os

from dotenv import load_dotenv
from flask import Response

from app import create_app

load_dotenv()

app = create_app(os.getenv('FLASK_CONFIG'))


@app.after_request
def after_request(response: Response) -> Response:
    """Registers a function to be run after each request.

    Parameters
    ----------
    response : Response
        A `flask.Response` instance.

    Returns
    -------
    Response
        A `flask.Response` instance.

    """
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    response.headers.add('Cache-Control', 'no-cache')
    return response


if __name__ == '__main__':
    app.run()
