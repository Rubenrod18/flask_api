import logging
import os
from datetime import datetime

from flask import Response
from flask_script import Manager
from dotenv import load_dotenv

from app import create_app
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

# App
app = create_app(os.getenv('FLASK_CONFIG'))
manager = Manager(app)


@app.after_request
def after_request(response: Response) -> Response:
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    response.headers.add('Cache-Control', 'no-cache')
    return response


@manager.command
def migrate():
    init_db()


@manager.command
def seed():
    init_seed()


if __name__ == '__main__':
    manager.run()
