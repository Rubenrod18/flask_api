import logging

from flask_restful import Api, Resource
from flask import Blueprint
from peewee import ModelSelect

from ..extensions import db_wrapper as db
from ..utils import get_request_query_fields, create_query

blueprint = Blueprint('base', __name__, url_prefix='/')
api = Api(blueprint)

logger = logging.getLogger(__name__)


class BaseResource(Resource):
    db_model: db.Model

    def get_request_query_fields(self, request_data: dict):
        return get_request_query_fields(self.db_model, request_data)

    def create_query(self, query: ModelSelect, request_data: dict):
        return create_query(self.db_model, query, request_data)


@api.resource('')
class WelcomeResource(Resource):
    def get(self) -> tuple:
        return 'Welcome to flask_api!', 200
