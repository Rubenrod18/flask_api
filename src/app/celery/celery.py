import os

from dotenv import load_dotenv

from app import create_app

from . import make_celery

load_dotenv()

flask_app = create_app(os.getenv('FLASK_CONFIG'))
celery = make_celery(flask_app)
