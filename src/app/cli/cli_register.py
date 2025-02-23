import os

import click
from flask import current_app, Flask

from app.cli.create_db_cli import CreateDatabaseCli
from app.cli.seeder_cli import SeederCli
from app.extensions import db


def init_app(app: Flask):
    @app.cli.command('create_db', help='Create database.')
    def create_database() -> None:
        """Command line script for creating the database."""
        seeder_cli = CreateDatabaseCli(db_uri=current_app.config['SQLALCHEMY_DATABASE_URI'])
        seeder_cli.run_command()

    @app.cli.command('seed', help='Fill database with fake data.')
    def seeds() -> None:
        """Command line script for filling database with fake data."""
        seeder_cli = SeederCli(db=db)
        seeder_cli.run_command()

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
        return {'app': app, 'db': db}

    # NOTE: sphinx-click only shows Click documentation in Sphinx.
    @app.cli.command('celery', help='Run Celery with an environment configuration.')
    @click.option(
        '--env',
        type=click.Choice(['config.DevConfig', 'config.TestConfig', 'config.ProdConfig'], case_sensitive=False),
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
