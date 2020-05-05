from celery.utils.log import get_task_logger

from app.celery.celery import app

logger = get_task_logger(__name__)


@app.task
def add(x, y):
    result = x + y
    logger.info(f'sum args: {x} + {y} = {result}')
    return result


@app.task
def mul(x, y):
    result = x * y
    logger.info(f'mul args: {x} * {y} = {result}')
    return result


@app.task
def xsum(numbers):
    result = sum(numbers)
    logger.info(f'xsum args: {numbers} = {result}')
    return sum(numbers)
