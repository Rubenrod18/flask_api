"""Main module runs the application.

The module runs the application on differents
configurations ( dev, prod, testing, etc ), run commands, etc.

.. note:: A ".env" file must to be created before start up the application.

Examples
--------

How to run the server::

    source ven/bin/activate
    python manage.py

.. note:: You can open a web browser and go to server name http://flask-api.prod:5000
    or the server name added to SERVER_NAME environment variable.

How to run a command::

    source venv/bin/activate
    flask init-db

"""
import os

import click
from flask import Response
from dotenv import load_dotenv

from app import create_app
from app.extensions import db_wrapper
from database import init_database
from database.migrations import init_migrations
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


@app.cli.command('init-db', help='Create database tables')
def db() -> None:
    init_database()


@app.cli.command('migrate', help='Update database schema')
def migrations() -> None:
    init_migrations(False)


@app.cli.command('migrate-rollback', help='Revert last migration saved in database')
def migrations() -> None:
    init_migrations(True)


@app.cli.command('seed', help='Fill database with fake data')
def seeds() -> None:
    init_seed()


@app.cli.command('celery', help='Run celery with test configuration by default or another expecified')
@click.option('--env', default='test')
def celery(env: str) -> None:
    os.environ['FLASK_CONFIG'] = 'config.TestConfig' if env == 'test' else env
    os.system('source venv/bin/activate && celery -A app.celery worker -l info')


@app.shell_context_processor
def make_shell_context() -> dict:
    """Returns the shell context for an interactive shell for this application.
    This runs all the registered shell context processors.

    To explore the data in your application, you can start an interactive Python
    shell with the shell command. An application context will be active,
    and the app instance will be imported.

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
    return {'app': app, 'db_wrapper': db_wrapper}


if __name__ == '__main__':
    app.run()
