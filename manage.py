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
    return {'app': app, 'db_wrapper': db_wrapper}


if __name__ == '__main__':
    app.run()
