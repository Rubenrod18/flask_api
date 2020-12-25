from flask_restx import Resource
from flask import Blueprint
from peewee import ModelSelect

from ..extensions import db_wrapper as db, api as root_api
from ..utils import get_request_query_fields, create_search_query

blueprint = Blueprint('base', __name__)
api = root_api.namespace('', description='Base endpoints')


class BaseResource(Resource):
    db_model = db.Model

    def get_request_query_fields(self, request_data: dict) -> tuple:
        return get_request_query_fields(self.db_model, request_data)

    def create_search_query(self, query: ModelSelect, request_data: dict) \
            -> ModelSelect:
        return create_search_query(self.db_model, query, request_data)


@api.route('/welcome')
class WelcomeResource(Resource):
    @api.doc(responses={200: 'Welcome to flask_api!'})
    def get(self) -> tuple:
        return 'Welcome to flask_api!', 200
