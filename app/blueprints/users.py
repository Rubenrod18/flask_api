# Standard library imports
import json
from datetime import datetime

# Related third party imports
import xlsxwriter
import magic
from flask_restful import current_app, Api, Resource
from flask import Blueprint, request, send_file
from playhouse.shortcuts import model_to_dict
from peewee import CharField, DateField, DateTimeField, IntegerField

# Local application/library specific imports
from ..extensions import db_wrapper as db
from ..models.user import User as UserModel
from ..utils import custom_converter, readable_converter


blueprint = Blueprint('users', __name__, url_prefix='/users')
api = Api(blueprint)


# TODO: improve this function
def get_query_fields(data):
    page_number = data.get('page_number') if 'page_number' in data else 1

    items_per_page = data.get('items_per_page') if 'items_per_page' in data else 10

    if 'order' in data and 'sort' in data:
        sort = data.get('sort')
        order = data.get('order')

        order_by = UserModel._meta.fields[sort]
        if order == 'desc':
            order_by = order_by.desc()
    else:
        order_by = UserModel.id.desc()

    return page_number, items_per_page, order_by

# TODO: improve this function
def create_query(query, data):
    if 'search' in data:
        filters = data.get('search')

        filters = [
            item for item in filters
            if 'field_value' in item and item.get('field_value') != ''
            ]

        for item in filters:
            field_name = item['field_name']
            field = UserModel._meta.fields[field_name]

            field_value = item['field_value']

            if isinstance(field, IntegerField):
                query = query.where(field == field_value)
            elif isinstance(field, CharField):
                field_value = field_value.__str__()
                value = '%{0}%'.format(field_value)
                # OR use the exponent operator. Note: you must include wildcards here:
                query = query.where(field ** value)
            elif isinstance(field, DateField):
                # TODO: WIP -> add field_operator
                pass
            elif isinstance(field, DateTimeField):
                # TODO: add field_operator
                pass

    return query

@api.resource('')
class UsersResource(Resource):
    def post(self):
        data = request.get_json()

        page_number, items_per_page, order_by = get_query_fields(data)

        query = UserModel.select()
        records_total = query.count()

        query = create_query(query, data)

        query = query.order_by(order_by)
        records_filtered = query.count()

        users_query = query.paginate(page_number, items_per_page).dicts()
        users_list = []
        for user in users_query:
            user_dict = {k: custom_converter(v) for (k, v) in user.items()}
            users_list.append(user_dict)

        return {
            'records_total': records_total,
            'records_filtered': records_filtered,
            'data': users_list,
        }

@api.resource('/xlsx')
class ExportUsersExcelResource(Resource):
    def get(self):
        def get_column_names():
            column_names =  [
                    column.name
                    for column in db.database.get_columns('users')
                    if column.name != 'id'
                ]

            return column_names

        def format_column_names(rows):
            formatted_column_names = [
                    column.title().replace('_', ' ')
                    for column in original_column_names
                ]

            rows.append(formatted_column_names)

            return None

        def get_users(column_names, page_number, items_per_page):
            select_fields = [
                    UserModel._meta.fields[column_name]
                    for column_name in column_names
                ]

            users_query = (UserModel
                           .select(*select_fields)
                           .paginate(page_number, items_per_page)
                           .dicts())

            return users_query

        def format_user_data(users_query, rows):
            users_list = []

            for user in users_query:
                user_dict = {
                    k: readable_converter(v)
                    for (k, v) in user.items()
                    }
                users_list.append(user_dict)

            for user_dict in users_list:
                user_values = list(user_dict.values())
                rows.append(user_values)

            return None

        def write_excel_rows(rows, workbook, worksheet):
            # Iterate over the data and write it out row by row.
            for i, row in enumerate(rows, 1):
                format = None

                if i == 1:
                    format = workbook.add_format({
                            'bold': True,
                            'bg_color': '#CCCCCC'
                        })
                elif i % 2 == 0:
                    format = workbook.add_format({
                            'bg_color': '#f1f1f1'
                        })

                range_cells = "A%s:I10" % i

                worksheet.write_row(range_cells, row, format)

        def adjust_each_column_width(rows, worksheet):
            lists = [
                [row[i] for row in rows]
                for i in range(len(rows))
                ]

            for i, v in enumerate(lists):
                v3 = [str(v2) for v2 in v]
                max_column_width = max(v3, key=len)
                max_column_width_len = len(max_column_width)

                worksheet.set_column(i, i + 1, max_column_width_len + 2)

        storage_dir = current_app.config.get('STORAGE_DIRECTORY')
        file_prefix = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        excel_filename = '{}/{}_users.xlsx'.format(storage_dir, file_prefix)

        page_number, items_per_page = 1, 10
        rows = []

        workbook = xlsxwriter.Workbook(excel_filename)
        worksheet = workbook.add_worksheet()

        original_column_names = get_column_names()
        format_column_names(rows)

        users_query = get_users(original_column_names, page_number, items_per_page)
        format_user_data(users_query, rows)

        # TODO: I need to improve this for doing dynamic
        #last_col_index = len(formatted_column_names)
        #last_col = '{}{}.'.format(chr(last_col_index), last_col_index)
        #cell_range = 'A1:I10'
        worksheet.autofilter('A1:I10')

        write_excel_rows(rows, workbook, worksheet)
        adjust_each_column_width(rows, worksheet)

        workbook.close()

        kwargs = {
            'filename_or_fp' : excel_filename,
            'mimetype' : magic.from_file(excel_filename, mime=True),
            'as_attachment' : True,
            'attachment_filename' : excel_filename
        }

        return send_file(**kwargs)

@api.resource('/pdf')
class ExportUsersPdfResource(Resource):
    def get(self):
        root_dir = current_app.config['ROOT_DIRECTORY']
        excel_filename = root_dir + '/users.xlsx'

        workbook = xlsxwriter.Workbook(excel_filename)
        worksheet = workbook.add_worksheet()

        fieldnames = [p.name for p in db.database.get_columns('users')]
        rows = [fieldnames]

        users = UserModel.select().paginate(1, 10)
        users_list = [model_to_dict(t, backrefs=True) for t in users]

        for p in users_list:
            list_values = list(p.values())
            rows.append(list_values)

        row, col = 0, 0
        # Iterate over the data and write it out row by row.
        for items in rows:
            col = 0
            for item in items:
                worksheet.write(row, col, item)
                col += 1
            row += 1

        workbook.close()

        # WIP

        return {}
