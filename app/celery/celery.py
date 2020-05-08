import os

from dotenv import load_dotenv

from app import create_app
from app.celery import init_celery

load_dotenv()

flask_app = create_app(os.getenv('FLASK_CONFIG'))
celery = init_celery(flask_app)

if __name__ == '__main__':
    celery.run()
