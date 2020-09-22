from celery import chord
from celery.result import AsyncResult
from celery.utils.log import get_task_logger
from flask import render_template, current_app
from flask_mail import Message

from app.celery import ContextTask
from app.celery.word.tasks import export_user_data_in_word
from app.celery.excel.tasks import export_user_data_in_excel
from app.extensions import mail, celery

logger = get_task_logger(__name__)


@celery.task(base=ContextTask)
def create_user_email(email_data) -> bool:
    logger.info(f'to: {email_data}')

    to = [email_data.get('email')]

    email_args = {
        'subject': 'Welcome to Flask Api!',
        'sender': 'hello@flaskapi.com',
        'recipients': to,
    }
    msg = Message(**email_args)
    msg.html = render_template('mails/new_user.html', **email_data)
    mail.send(msg)
    return True


@celery.task(base=ContextTask)
def reset_password_email(email_data) -> bool:
    logger.info(f'to: {email_data}')

    to = [email_data.get('email')]

    email_args = {
        'subject': 'Reset password',
        'sender': 'noreply@flaskapi.com',
        'recipients': to,
    }
    msg = Message(**email_args)
    msg.html = render_template('mails/reset_password.html', **email_data)
    mail.send(msg)
    return True


@celery.task(base=ContextTask)
def send_email_with_attachments(task_data: list) -> bool:
    auth_user_data = task_data[0].get('result').get('created_by')

    to = [auth_user_data.get('email')]
    email_args = {
        'subject': 'Excel and word documents',
        'sender': 'noreply@flaskapi.com',
        'recipients': to,
    }

    msg = Message(**email_args)
    msg.html = render_template('mails/attachments.html', **auth_user_data)

    for item in task_data:
        document = item.get('result')

        directory_path = current_app.config.get('STORAGE_DIRECTORY')
        filepath = '%s/%s' % (directory_path,
                              document.get('internal_filename'))
        filename = document.get('name')

        with open(filepath, 'rb') as fp:
            msg.attach(filename, document.get('mime_type'),
                       fp.read())

    mail.send(msg)
    return True


@celery.task(base=ContextTask)
def create_word_and_excel_documents(created_by: int, request_data: dict,
                                    to_pdf: int) -> None:
    group_tasks = [
        export_user_data_in_word.s(created_by, request_data, to_pdf),
        export_user_data_in_excel.s(created_by, request_data),
    ]
    callback_task = send_email_with_attachments.s()

    chord(group_tasks, callback_task)()
