import xlsxwriter
import magic
from flask_restful import current_app, Api, Resource
from flask import Blueprint, send_file
from playhouse.shortcuts import model_to_dict

from ..extensions import db_wrapper as db
from ..models.person import Person as PersonModel

blueprint = Blueprint('people', __name__, url_prefix='/people')
api = Api(blueprint)


@api.resource('')
class PeopleResource(Resource):
    def get(self):
        people = PersonModel.select().paginate(1, 10)

        people_list = [model_to_dict(t, backrefs=True) for t in people]

        return {
            'data': people_list
        }

@api.resource('/xlsx')
class ExportPeopleExcelResource(Resource):
    def get(self):
        root_dir = current_app.config['ROOT_DIRECTORY']
        excel_filename = root_dir + '/people.xlsx'

        workbook = xlsxwriter.Workbook(excel_filename)
        worksheet = workbook.add_worksheet()

        fieldnames = [p.name for p in db.database.get_columns('person')]
        rows = [fieldnames]

        people = PersonModel.select().paginate(1, 10)
        people_list = [model_to_dict(t, backrefs=True) for t in people]

        for p in people_list:
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
