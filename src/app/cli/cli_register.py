from flask import Flask

from app.cli.create_db_cli import CreateDatabaseCli
from app.database.seeds import init_seed
from app.extensions import db


def init_app(app: Flask):
    @app.cli.command('create_db', help='Create database.')
    def create_database() -> None:
        """Command line script for creating the database."""
        seeder_cli = CreateDatabaseCli()
        seeder_cli.run_command()

    @app.cli.command('seed', help='Fill database with fake data.')
    def seeds() -> None:
        """Command line script for filling database with fake data."""
        init_seed()

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
