import mimetypes
import os
import uuid
from datetime import datetime
from tempfile import NamedTemporaryFile

import docx
from celery.utils.log import get_task_logger
from flask import current_app

from app.celery import ContextTask
from app.extensions import celery
from app.libs.libreoffice import convert_to
from app.models.document import Document as DocumentModel
from app.models.user import User as UserModel
from app.utils import to_readable
from app.utils.file_storage import FileStorage

logger = get_task_logger(__name__)

column_display_order = ['name', 'last_name', 'email', 'birth_date', 'role', 'created_at', 'updated_at',
                        'deleted_at']


def _format_user_data(users_query: list, rows: list) -> None:
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


def _format_column_names(rows: list, original_column_names: set) -> None:
    formatted_column_names = [
        column.title().replace('_', ' ')
        for column in original_column_names
        if column
    ]

    rows.append(formatted_column_names)


@celery.task(bind=True, base=ContextTask)
def user_data_export_in_word(self, created_by: int, user_list: list, to_pdf: bool = False):
    def _write_docx_content(rows: list, document: docx.Document) -> None:
        header_fields = rows[0]

        table = document.add_table(rows=len(rows), cols=len(header_fields))

        for i in range(len(rows)):
            row = table.rows[i]
            for j, table_cell in enumerate(rows[i]):
                row.cells[j].text = str(table_cell)

            self.update_state(state='PROGRESS', meta={
                'current': i,
                'total': self.total_progress,
                'status': 'In progress...',
            })

    self.total_progress = len(user_list) + 2  # Word table rows + 2 (Word table header and save Word in database)
    tempfile_suffix = '.docx'
    tempfile = NamedTemporaryFile(suffix=tempfile_suffix)
    excel_rows = []
    mime_type = 'application/pdf' if to_pdf else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

    self.update_state(state='PROGRESS', meta={
        'current': 0,
        'total': self.total_progress,
        'status': 'In progress...',
    })

    # TODO: insert query for getting users here

    original_column_names = UserModel.get_fields(exclude=['id', 'password'],
                                                 include=column_display_order,
                                                 sort_order=column_display_order)
    _format_column_names(excel_rows, original_column_names)
    _format_user_data(user_list, excel_rows)

    document = docx.Document()
    _write_docx_content(excel_rows, document)
    document.save(tempfile.name)

    directory_path = current_app.config.get('STORAGE_DIRECTORY')
    temp_filename = FileStorage.get_basename(tempfile.name, include_path=False)

    if to_pdf:
        convert_to(directory_path, tempfile.name)
    else:
        dst = f'{directory_path}/{temp_filename}{tempfile_suffix}'
        FileStorage.copy_file(tempfile.name, dst)

    file_extension = mimetypes.guess_extension(mime_type)
    internal_filename = '%s%s' % (uuid.uuid1().hex, file_extension)
    filepath = '%s/%s' % (directory_path, internal_filename)

    try:
        file_prefix = datetime.utcnow().strftime('%Y%m%d')
        basename = f'{file_prefix}_users'
        filename = f'{basename}{file_extension}'

        src = '%s/%s%s' % (directory_path, temp_filename, file_extension)
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
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        logger.debug(e)
        raise e

    return {
        'current': self.total_progress,
        'total': self.total_progress,
        'status': 'Task completed!',
        'result': document.serialize(),
    }
