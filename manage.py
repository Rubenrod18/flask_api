import os

from flask import Response
from dotenv import load_dotenv

from app import create_app, init_logging
from app.extensions import db_wrapper
from database.migrations import init_database, init_migrations
from database.seeds import init_seed

load_dotenv()

app = create_app(os.getenv('FLASK_CONFIG'))

init_logging(app)


@app.after_request
def after_request(response: Response) -> Response:
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    response.headers.add('Cache-Control', 'no-cache')
    return response


@app.cli.command('init-db')
def db():
    init_database()


@app.cli.command('migrate')
def migrations():
    init_migrations(False)


@app.cli.command('migrate-rollback')
def migrations():
    init_migrations(True)


@app.cli.command('seed')
def seeds():
    init_seed()


@app.shell_context_processor
def make_shell_context():
    return {'app': app, 'db_wrapper': db_wrapper}


if __name__ == '__main__':
    app.run()
