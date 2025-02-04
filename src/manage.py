"""Main module runs the application.

The module runs the application on differents
configurations ( dev, prod, testing, etc ), run commands, etc.

.. note:: A ".env" file must to be created before start up the
application.

Examples
--------

How to run the server::

    source ven/bin/activate
    python manage.py

.. note:: You can open a web browser and go to server name
    http://flask-api.prod:5000 or the server name added to SERVER_NAME
    environment variable.

How to run a command::

    source venv/bin/activate
    flask init-db

"""
import os

import click
from dotenv import load_dotenv
from flask import Response

from app import create_app
from app.extensions import db
from database.factories import Factory
from database.seeds import init_seed

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


@app.cli.command('seed', help='Fill database with fake data.')
def seeds() -> None:
    """Command line script for filling database with fake data."""
    init_seed()


# TODO: sphinx-click only shows Click documentation in Sphinx.
@app.cli.command('celery', help='Run Celery with an environment configuration.')
@click.option(
    '--env',
    type=click.Choice(
        ['config.DevConfig', 'config.TestConfig', 'config.ProdConfig'], case_sensitive=False
    ),
    default='config.TestConfig',
    show_default=True,
    help='Environment configuration.',
)
def celery(env: str) -> None:
    """Command line script for executing Celery based on FLASK_CONFIG
    environment value.

    The command line script purpose is executing Celery in testing mode
    because we don't want to do operations such as: send emails,
    communicate with other API's, etc. You can choose another
    environment if you wish.

    Parameters
    ----------
    env : str
        Environment configuration.

    Notes
    -----
    First you must to starting a broker such as: RabbitMQ, Redis, etc.

    Environment configuration values could be::

            config.ProdConfig
            config.DevConfig
            config.TestConfig

    Examples
    --------
    Testing environment is used by default::

        source venv/bin/activate
        flask celery

    You can use production environment::

        source venv/bin/activate
        flask celery --env config.ProdConfig

    Or development environment::

        source venv/bin/activate
        flask celery --env config.DevConfig

    """
    os.environ['FLASK_CONFIG'] = env
    os.system('celery -A app.celery worker -l info --events')


@app.shell_context_processor
def make_shell_context() -> dict:
    """Returns the shell context for an interactive shell for this
    application.

    This runs all the registered shell context processors.

    To explore the data in your application, you can start an
    interactive Python shell with the shell command. An application
    context will be active, and the app instance will be imported.

    How to usage::

        source venv/bin/activate
        flask shell

    .. _shell_context_processor:
        https://flask.palletsprojects.com/en/1.1.x/cli/#open-a-shell

    Returns
    -------
    dict
        Imports available in Python shell.

    """
    return {'app': app, 'db': db, 'Factory': Factory}


if __name__ == '__main__':
    app.run()
