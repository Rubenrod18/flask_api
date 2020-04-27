from flask_restful import Api, Resource
from flask import Blueprint, request
from peewee import ModelSelect, IntegerField, CharField, DateField, DateTimeField

from ..extensions import db_wrapper as db

blueprint = Blueprint('base', __name__, url_prefix='/')
api = Api(blueprint)

class BaseResource(Resource):
    db_model: db.Model

    def get_request_query_fields(self, request_data=None) -> tuple:
        if request_data is None:
            request_data = request.get_json() or {}

        # Page numbers are 1-based, so the first page of results will be page 1.
        # http://docs.peewee-orm.com/en/latest/peewee/querying.html#paginating-records
        tmp = int(request_data.get('page_number', 1))
        page_number = 1 if tmp < 1 else tmp

        tmp = int(request_data.get('items_per_page', 10))
        items_per_page = 10 if tmp < 1 else tmp

        sort = request_data.get('sort', 'id')
        order = request_data.get('order', 'asc')

        order_by = self.db_model._meta.fields[sort]

        if order == 'desc':
            order_by = order_by.desc()

        return page_number, items_per_page, order_by

    def create_query(self, query: ModelSelect = ModelSelect, data: dict = None) -> ModelSelect:
        if data is None:
            data = {}

        search_data = data.get('search', {})

        filters = [
            item for item in search_data
            if 'field_value' in item and item.get('field_value') != ''
        ]

        for filter in filters:
            field_name = filter['field_name']
            field = self.db_model._meta.fields[field_name]

            field_value = filter['field_value']

            if isinstance(field, IntegerField):
                query = query.where(field == field_value)
            elif isinstance(field, CharField):
                field_value = field_value.__str__()
                value = '%{0}%'.format(field_value)
                # OR use the exponent operator.
                # Note: you must include wildcards here:
                query = query.where(field ** value)
            elif isinstance(field, DateField):
                # TODO: WIP -> add field_operator
                pass
            elif isinstance(field, DateTimeField):
                # TODO: add field_operator
                pass

        return query

@api.resource('')
class WelcomeResource(Resource):
    def get(self) -> tuple:
        return 'Welcome to flask_api!', 200
