# Standard library imports
import json

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
from ..utils import custom_converter


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
            if 'field_value' in item and not item.get('field_value')
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

        kwargs = {
            'filename_or_fp' : excel_filename,
            'mimetype' : magic.from_file(excel_filename, mime=True),
            'as_attachment' : True,
            'attachment_filename' : excel_filename
        }

        return send_file(**kwargs)
