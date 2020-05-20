import mimetypes
import os
import uuid
from datetime import datetime
from tempfile import NamedTemporaryFile

import docx
from celery.utils.log import get_task_logger
from flask import render_template, current_app
from flask_mail import Message

from app.celery import ContextTask
from app.extensions import mail, celery
from app.libs.libreoffice import convert_to
from app.models.document import Document as DocumentModel
from app.models.user import User as UserModel
from app.utils import to_readable
from app.utils.file_storage import FileStorage

logger = get_task_logger(__name__)

column_display_order = ['name', 'last_name', 'email', 'birth_date', 'role', 'created_at', 'updated_at',
                        'deleted_at']


def format_user_data(users_query: list, rows: list) -> None:
    user_list = []

    for user in users_query:
        user_dict = {
            'role': user.get('role').get('name'),
        }
        del user['role']

        user_dict.update({
            k: to_readable(v)
            for (k, v) in user.items()
            if k in column_display_order
        })

        user_dict = dict(sorted(user_dict.items(), key=lambda x: column_display_order.index(x[0])))
        user_list.append(user_dict)

    for user_dict in user_list:
        user_values = list(user_dict.values())
        rows.append(user_values)


def format_column_names(rows: list, original_column_names: set) -> None:
    formatted_column_names = [
        column.title().replace('_', ' ')
        for column in original_column_names
        if column
    ]

    rows.append(formatted_column_names)


@celery.task(name='create_user_email', base=ContextTask)
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


@celery.task(name='reset_password_email', base=ContextTask)
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


@celery.task(bind=True, name='export_users_pdf', base=ContextTask)
def export_users_pdf(self, created_by: int, user_list: list):
    def write_docx_content(rows: list, document: docx.Document) -> None:
        header_fields = rows[0]

        table = document.add_table(rows=len(rows), cols=len(header_fields))

        for i in range(len(rows)):
            row = table.rows[i]
            for j, table_cell in enumerate(rows[i]):
                row.cells[j].text = str(table_cell)

            self.update_state(state='PROGRESS', meta={
                'current': i,
                'total': self.total,
                'status': 'In progress...',
            })

    self.total = len(user_list) + 2
    tempfile = NamedTemporaryFile(suffix='.docx')
    excel_rows = []

    original_column_names = UserModel.get_fields(exclude=['id', 'password'],
                                                 include=column_display_order,
                                                 sort_order=column_display_order)
    format_column_names(excel_rows, original_column_names)
    format_user_data(user_list, excel_rows)

    document = docx.Document()
    write_docx_content(excel_rows, document)
    document.save(tempfile.name)

    directory_path = current_app.config.get('STORAGE_DIRECTORY')
    convert_to(directory_path, tempfile.name)

    mime_type = 'application/pdf'
    file_extension = mimetypes.guess_extension(mime_type)

    internal_filename = '%s%s' % (uuid.uuid1().hex, file_extension)
    filepath = '%s/%s' % (directory_path, internal_filename)

    try:
        file_prefix = datetime.utcnow().strftime('%Y%m%d')
        basename = f'{file_prefix}_users'
        filename = f'{basename}{file_extension}'

        src = '%s/%s%s' % (directory_path, FileStorage.get_basename(tempfile.name, include_path=False), file_extension)
        FileStorage.rename(src, filepath)

        data = {
            'created_by': created_by,
            'name': filename,
            'internal_filename': internal_filename,
            'mime_type': mime_type,
            'directory_path': directory_path,
            'size': FileStorage.get_filesize(filepath),
        }

        document = DocumentModel.create(**data)
        tempfile.close()
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        logger.debug(e)
        raise e

    return {'current': self.total, 'total': self.total, 'status': 'Task completed!', 'result': document.url}
