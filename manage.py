import logging
import os
from datetime import datetime

from flask import Response
from dotenv import load_dotenv

from app import create_app
from app.extensions import db_wrapper as db
from database.migrations import init_db
from database.seeds import init_seed

# Import environment file variables
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


@app.cli.command('migrate')
def migrate():
    init_db()


@app.cli.command('seed')
def seed():
    init_seed()


if __name__ == '__main__':
    app.run()
