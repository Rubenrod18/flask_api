import logging
import os
import sys

from dotenv import load_dotenv

from app import create_app

from . import make_celery

load_dotenv()

# NOTE: Set up basic logging early to ensure all components (Flask, Celery, etc.)
#       log consistently to stdout, especially useful in Docker environments.
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
)
logger = logging.getLogger(__name__)
logger.info(f' Application environment: {os.getenv("FLASK_CONFIG")}')

flask_app = create_app(os.getenv('FLASK_CONFIG'))
celery = make_celery(flask_app)
