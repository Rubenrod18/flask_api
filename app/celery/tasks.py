import mimetypes
import os
import time
import uuid
from datetime import datetime
from tempfile import NamedTemporaryFile

import docx
import xlsxwriter
from celery.utils.log import get_task_logger
from flask import render_template, current_app
from flask_mail import Message
from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet

from app.celery import ContextTask
from app.extensions import mail, celery
from app.libs.libreoffice import convert_to
from app.models.document import Document as DocumentModel
from app.models.user import User as UserModel
from app.utils import pos_to_char, find_longest_word, to_readable
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


@celery.task(bind=True, name='export_users_excel', base=ContextTask)
def export_users_excel(self, created_by: int, user_list: list):
    def write_excel_rows(rows: list, workbook: Workbook, worksheet: Worksheet) -> int:
        excel_longest_word = ''

        for i, row in enumerate(rows, 1):
            format = None

            if i == 1:
                format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#cccccc',
                })
            elif i % 2 == 0:
                format = workbook.add_format({
                    'bg_color': '#f1f1f1',
                })

            range_cells = 'A%s:I10' % i

            row_longest_word = find_longest_word(row)
            if len(row_longest_word) > len(excel_longest_word):
                excel_longest_word = row_longest_word

            worksheet.write_row(range_cells, row, format)
            self.update_state(state='PROGRESS', meta={
                'current': i,
                'total': self.total,
                'status': 'In progress...',
            })
            time.sleep(2)

        return len(excel_longest_word)

    def adjust_each_column_width(rows: list, worksheet: Worksheet, excel_longest_word: int) -> None:
        if rows:
            for i, v in enumerate(rows[0]):
                worksheet.set_column(i, i + 1, excel_longest_word + 1)

    self.total = len(user_list) + 2
    tempfile = NamedTemporaryFile()
    excel_rows = []

    workbook = xlsxwriter.Workbook(tempfile.name)
    worksheet = workbook.add_worksheet()
    worksheet.set_zoom(120)

    original_column_names = UserModel.get_fields(exclude=['id', 'password'],
                                                 include=column_display_order,
                                                 sort_order=column_display_order)
    format_column_names(excel_rows, original_column_names)
    format_user_data(user_list, excel_rows)

    total_fields = len(UserModel.get_fields(exclude=['id', 'password'], include=column_display_order)) - 1
    columns = 'A1:%s10' % pos_to_char(total_fields).upper()
    worksheet.autofilter(columns)

    excel_longest_word = write_excel_rows(excel_rows, workbook, worksheet)
    adjust_each_column_width(excel_rows, worksheet, excel_longest_word)

    workbook.close()

    mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    file_extension = mimetypes.guess_extension(mime_type)

    internal_filename = '%s%s' % (uuid.uuid1().hex, file_extension)
    directory_path = current_app.config.get('STORAGE_DIRECTORY')
    filepath = f'{directory_path}/{internal_filename}'

    try:
        fs = FileStorage()
        fs.save_bytes(tempfile.read(), filepath)

        file_prefix = datetime.utcnow().strftime('%Y%m%d')
        basename = f'{file_prefix}_users'
        filename = f'{basename}.{file_extension}'

        data = {
            'created_by': created_by,
            'name': filename,
            'internal_filename': internal_filename,
            'mime_type': mime_type,
            'directory_path': directory_path,
            'size': fs.get_filesize(filepath),
        }

        document = DocumentModel.create(**data)
        tempfile.close()
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        logger.debug(e)
        raise e

    return {'current': self.total, 'total': self.total, 'status': 'Task completed!', 'result': document.url}


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
            time.sleep(2)

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
