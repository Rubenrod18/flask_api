import time

from celery.utils.log import get_task_logger

from app.celery.celery import celery

logger = get_task_logger(__name__)


@celery.task(name='hello_world')
def hello_world():
    logger.info(f'task id: %s' % hello_world.request.id)
    time.sleep(5)
    return 'Hello workd'
