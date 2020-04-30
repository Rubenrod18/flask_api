import os

from flask import Response
from flask_script import Manager
from dotenv import load_dotenv

from app import create_app, init_logging
from database.migrations import init_db
from database.seeds import init_seed

load_dotenv()

app = create_app(os.getenv('FLASK_CONFIG'))
manager = Manager(app)

init_logging(app)


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
