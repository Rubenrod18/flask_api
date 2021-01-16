import os

from dotenv import load_dotenv

from app import create_app
from app.extensions import celery

load_dotenv()

print('Environment: %s' % os.getenv('FLASK_CONFIG'))
flask_app = create_app(os.getenv('FLASK_CONFIG'))
celery.init_app(flask_app)

if __name__ == '__main__':
    celery.run()
