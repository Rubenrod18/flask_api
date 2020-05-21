import os

from flask import Response
from dotenv import load_dotenv

from app import create_app, init_logging
from app.extensions import db_wrapper
from app.utils.middleware import middleware
from database import init_database
from database.migrations import init_migrations
from database.seeds import init_seed

load_dotenv()

app = create_app(os.getenv('FLASK_CONFIG'))
app.wsgi_app = middleware(app.wsgi_app)

init_logging(app)


@app.after_request
def after_request(response: Response) -> Response:
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    response.headers.add('Cache-Control', 'no-cache')
    return response


@app.cli.command('init-db', help='Create database tables')
def db():
    init_database()


@app.cli.command('migrate', help='Update database schema')
def migrations():
    init_migrations(False)


@app.cli.command('migrate-rollback', help='Revert last migration saved in database')
def migrations():
    init_migrations(True)


@app.cli.command('seed', help='Fill database with fake data')
def seeds():
    init_seed()


@app.shell_context_processor
def make_shell_context():
    return {'app': app, 'db_wrapper': db_wrapper}


if __name__ == '__main__':
    app.run()
