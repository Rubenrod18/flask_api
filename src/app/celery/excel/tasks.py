import mimetypes
import uuid
from datetime import datetime, UTC
from tempfile import NamedTemporaryFile

import magic
import xlsxwriter
from celery import states
from celery.utils.log import get_task_logger
from flask import current_app
from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet

from app.celery import ContextTask
from app.extensions import celery, db
from app.file_storages import LocalStorage
from app.helpers.sqlalchemy_query_builder import SQLAlchemyQueryBuilder
from app.models import Document, User
from app.serializers import DocumentSerializer, UserSerializer
from app.utils import to_readable

logger = get_task_logger(__name__)

_COLUMN_DISPLAY_ORDER = [
    'name',
    'last_name',
    'email',
    'birth_date',
    'role',
    'created_at',
    'updated_at',
    'deleted_at',
]
_EXCLUDE_COLUMNS = ['id', 'password']


def _parse_user_data(users: list) -> list:
    excel_rows = []

    for user in users:
        user_dict = {
            'role': user.get('roles')[0].get('label'),
        }
        del user['roles']

        user_dict.update({k: to_readable(v) for (k, v) in user.items() if k in _COLUMN_DISPLAY_ORDER})

        user_dict = dict(sorted(user_dict.items(), key=lambda x: _COLUMN_DISPLAY_ORDER.index(x[0])))
        excel_rows.append(user_dict)

    return excel_rows


def _get_excel_user_data(users: list, excel_rows: list) -> None:
    parser_user_data = _parse_user_data(users)

    for user in parser_user_data:
        user_values = list(user.values())
        excel_rows.append(user_values)


def _get_excel_column_names(excel_rows: list) -> None:
    column_names = [column.title().replace('_', ' ') for column in _COLUMN_DISPLAY_ORDER if column]

    excel_rows.append(column_names)


def _adjust_each_column_width(rows: list, worksheet: Worksheet, excel_longest_word: int) -> None:
    if rows:
        for i, _ in enumerate(rows[0]):
            worksheet.set_column(i, i + 1, excel_longest_word + 1)


def _add_excel_autofilter(worksheet: Worksheet) -> None:
    total_fields = len(_COLUMN_DISPLAY_ORDER)
    pos_to_char = chr(total_fields + 97).upper()
    columns = f'A1:{pos_to_char}10'
    worksheet.autofilter(columns)


def _get_user_data(request_data: dict) -> list:
    rqo = SQLAlchemyQueryBuilder()
    page_number, items_per_page, order_by = rqo.get_request_query_fields(User, request_data)

    query = db.session.query(User)
    query = rqo.create_search_query(User, query, request_data)
    query = query.order_by(*order_by).offset(page_number * items_per_page).limit(items_per_page)

    user_serializer = UserSerializer(many=True)
    user_list = user_serializer.dump(list(query))

    return user_list


def _find_longest_word(word_list: list) -> str:
    str_list = [str(item) for item in word_list]
    longest_word = max(str_list, key=len)
    return str(longest_word)


def export_user_data_in_excel_task_logic(self, created_by: int, request_data: dict):
    def _write_excel_rows(rows: list, workbook: Workbook, worksheet: Worksheet) -> int:
        excel_longest_word = ''

        for i, row in enumerate(rows, 1):
            row_format = None

            if i == 1:
                row_format = workbook.add_format(
                    {
                        'bold': True,
                        'bg_color': '#cccccc',
                    }
                )
            elif i % 2 == 0:
                row_format = workbook.add_format(
                    {
                        'bg_color': '#f1f1f1',
                    }
                )

            range_cells = f'A{i}:I10'

            row_longest_word = _find_longest_word(row)
            if len(row_longest_word) > len(excel_longest_word):
                excel_longest_word = row_longest_word

            worksheet.write_row(range_cells, row, row_format)
            self.update_state(state=states.STARTED, meta={'current': i, 'total': self.total_progress})

        return len(excel_longest_word)

    local_storage = LocalStorage()
    user_list = _get_user_data(request_data)

    # Excel rows + 2 (Excel header row and save data in database)
    self.total_progress = len(user_list) + 2
    tempfile = NamedTemporaryFile()
    excel_rows = []

    self.update_state(state=states.STARTED, meta={'current': 0, 'total': self.total_progress})

    workbook = xlsxwriter.Workbook(tempfile.name)
    worksheet = workbook.add_worksheet()
    worksheet.set_zoom(120)

    _get_excel_column_names(excel_rows)
    _get_excel_user_data(user_list, excel_rows)
    _add_excel_autofilter(worksheet)

    excel_longest_word = _write_excel_rows(excel_rows, workbook, worksheet)
    _adjust_each_column_width(excel_rows, worksheet, excel_longest_word)
    workbook.close()

    filepath = ''
    try:
        mime_type = magic.from_file(tempfile.name, mime=True)
        file_extension = mimetypes.guess_extension(mime_type)

        internal_filename = f'{uuid.uuid1().hex}{file_extension}'
        directory_path = current_app.config.get('STORAGE_DIRECTORY')
        filepath = f'{directory_path}/{internal_filename}'

        data = tempfile.file.read()
        local_storage.save_bytes(data, filepath)

        file_prefix = datetime.now(UTC).strftime('%Y%m%d')
        basename = f'{file_prefix}_users'
        filename = f'{basename}{file_extension}'

        data = {
            'created_by': created_by,
            'name': filename,
            'internal_filename': internal_filename,
            'mime_type': mime_type,
            'directory_path': directory_path,
            'size': local_storage.get_filesize(filepath),
        }

        document = Document(**data)
        db.session.add(document)
        db.session.flush()
    except Exception as e:
        db.session.rollback()
        local_storage.delete_file(filepath)
        logger.debug(e)
        raise

    document_serializer = DocumentSerializer(exclude=('internal_filename',))
    document_data = document_serializer.dump(document)
    db.session.commit()

    return {
        'current': self.total_progress,
        'total': self.total_progress,
        'status': 'Task completed!',
        'result': document_data,
    }


@celery.task(bind=True, base=ContextTask, queue='fast')
def export_user_data_in_excel_task(self, created_by: int, request_data: dict):
    # HACK: Consider to move self logic outside of task_logic function.
    #       It helps both maintainability and testability.
    return export_user_data_in_excel_task_logic(self, created_by, request_data)
