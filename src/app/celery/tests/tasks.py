from flask import current_app

from app.celery import ContextTask
from app.extensions import celery
from app.models import Base


@celery.task(base=ContextTask)
def create_task_table() -> None:
    sql_file = ('%s/create_task_table.sql'
                % current_app.config.get('MOCKUP_DIRECTORY'))
    with open(sql_file, 'r') as fp:
        sql = fp.read()
    Base.raw(sql)


@celery.task(base=ContextTask)
def insert_task_record() -> None:
    sql_file = ('%s/create_task_record.sql'
                % current_app.config.get('MOCKUP_DIRECTORY'))
    with open(sql_file, 'r') as fp:
        sql = fp.read()
    Base.raw(sql)
