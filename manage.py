import logging
import os
from datetime import datetime

import click
from flask import Response
from dotenv import load_dotenv

from app import create_app
from app.extensions import db_wrapper
from database.migrations import init_database, init_migrations
from database.seeds import init_seed

load_dotenv()

# Log configuration
log_dirname = 'logs/'
log_filename = '{}.log'.format(datetime.utcnow().strftime('%Y%m%d'))
log_fullpath = '{}{}'.format(log_dirname, log_filename)

if not os.path.exists(log_dirname):
    os.mkdir(log_dirname)

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(filename=log_fullpath, format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = create_app(os.getenv('FLASK_CONFIG'))


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
