from celery import chain, chord
from celery.utils.log import get_task_logger
from flask import render_template
from flask_mail import Message

from app.celery import ContextTask
from app.celery.excel.tasks import export_user_data_in_excel_task
from app.celery.word.tasks import export_user_data_in_word_task
from app.extensions import celery, db, mail
from app.repositories import DocumentRepository
from config import Config

logger = get_task_logger(__name__)


@celery.task(base=ContextTask)
def create_user_email_task(email_data) -> bool:
    email_data.update({'login_url': f'http://{Config.SERVER_NAME}'})

    msg = Message(
        **{
            'subject': 'Welcome to Flask Api!',
            'sender': 'hello@flaskapi.com',
            'recipients': [email_data.get('email')],
        }
    )
    msg.html = render_template('mails/new_user.html', **email_data)
    mail.send(msg)
    return True


@celery.task(base=ContextTask)
def reset_password_email_task(email_data) -> bool:
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
def send_email_with_attachments_task(task_data: list) -> bool:
    document_repository = DocumentRepository()
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
        document = document_repository.find_by_id(item.get('result')['id'])
        with open(document.get_filepath(), 'rb') as fp:
            msg.attach(document.name, document.mime_type, fp.read())

    mail.send(msg)
    return True


@celery.task(base=ContextTask, queue='fast')
def create_word_and_excel_documents_task(created_by: int, request_data: dict, to_pdf: int) -> bool:
    group_tasks = [
        export_user_data_in_word_task.s(created_by, request_data, to_pdf),
        export_user_data_in_excel_task.s(created_by, request_data),
    ]
    callback_task = send_email_with_attachments_task.s()
    callback_result = chord(chain(*group_tasks))(callback_task)

    if callback_result.successful():
        db.session.commit()
    else:
        db.session.rollback()

    db.session.close()
    return True
