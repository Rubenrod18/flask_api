import mimetypes
import os
import uuid
from datetime import datetime
from tempfile import NamedTemporaryFile

import magic
import xlsxwriter
from celery.utils.log import get_task_logger
from flask import current_app
from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet

from app.celery import ContextTask
from app.extensions import celery
from app.models.document import Document as DocumentModel
from app.models.user import User as UserModel
from app.utils import find_longest_word, pos_to_char, to_readable
from app.utils.file_storage import FileStorage

logger = get_task_logger(__name__)

_COLUMN_DISPLAY_ORDER = ['name', 'last_name', 'email', 'birth_date', 'role', 'created_at', 'updated_at',
                         'deleted_at', ]
_EXCLUDE_COLUMNS = ['id', 'password', ]


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
            if k in _COLUMN_DISPLAY_ORDER
        })

        user_dict = dict(sorted(user_dict.items(), key=lambda x: _COLUMN_DISPLAY_ORDER.index(x[0])))
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


def _adjust_each_column_width(rows: list, worksheet: Worksheet, excel_longest_word: int) -> None:
    if rows:
        for i, v in enumerate(rows[0]):
            worksheet.set_column(i, i + 1, excel_longest_word + 1)


def _table_header_setup(worksheet: Worksheet):
    total_fields = len(UserModel.get_fields(exclude=_EXCLUDE_COLUMNS, include=_COLUMN_DISPLAY_ORDER)) - 1
    columns = 'A1:%s10' % pos_to_char(total_fields).upper()
    worksheet.autofilter(columns)


@celery.task(bind=True, base=ContextTask)
def user_data_export_in_excel(self, created_by: int, user_list: list):
    def _write_excel_rows(rows: list, workbook: Workbook, worksheet: Worksheet) -> int:
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
                'total': self.total_progress,
                'status': 'In progress...',
            })

        return len(excel_longest_word)

    self.total_progress = len(user_list) + 2  # Excel table rows + 2 (Excel table header and save Excel in database)
    tempfile = NamedTemporaryFile()
    excel_rows = []

    self.update_state(state='PROGRESS', meta={
        'current': 0,
        'total': self.total_progress,
        'status': 'In progress...',
    })

    # TODO: insert query for getting users here

    workbook = xlsxwriter.Workbook(tempfile.name)
    worksheet = workbook.add_worksheet()
    worksheet.set_zoom(120)

    original_column_names = UserModel.get_fields(exclude=_EXCLUDE_COLUMNS,
                                                 include=_COLUMN_DISPLAY_ORDER,
                                                 sort_order=_COLUMN_DISPLAY_ORDER)
    _format_column_names(excel_rows, original_column_names)
    _format_user_data(user_list, excel_rows)
    _table_header_setup(worksheet)

    excel_longest_word = _write_excel_rows(excel_rows, workbook, worksheet)
    _adjust_each_column_width(excel_rows, worksheet, excel_longest_word)
    workbook.close()

    filepath = ''
    try:
        mime_type = magic.from_file(tempfile.name, mime=True)
        file_extension = mimetypes.guess_extension(mime_type)

        internal_filename = '%s%s' % (uuid.uuid1().hex, file_extension)
        directory_path = current_app.config.get('STORAGE_DIRECTORY')
        filepath = f'{directory_path}/{internal_filename}'

        data = tempfile.file.read()
        fs = FileStorage()
        fs.save_bytes(data, filepath)

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
    except Exception:
        if os.path.exists(filepath):
            os.remove(filepath)
        raise

    return {
        'current': self.total_progress,
        'total': self.total_progress,
        'status': 'Task completed!',
        'result': document.serialize(),
    }
