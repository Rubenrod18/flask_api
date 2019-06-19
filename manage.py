import os

from flask_script import Manager

from app import create_app
from app.models import *

app = create_app(os.getenv('FLASK_CONFIG', 'config.DevConfig'))
manager = Manager(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    response.headers.add('Cache-Control', 'no-cache')
    return response

if __name__ == '__main__':
    manager.run()
