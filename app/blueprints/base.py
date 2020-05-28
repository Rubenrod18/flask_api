import collections
import logging
from operator import itemgetter

from flask_restful import Api, Resource
from flask import Blueprint, current_app
from peewee import ModelSelect
from werkzeug.exceptions import UnprocessableEntity

from ..extensions import db_wrapper as db
from ..utils import get_request_query_fields, create_search_query
from ..utils.cerberus_schema import MyValidator

blueprint = Blueprint('base', __name__, url_prefix='/')
api = Api(blueprint)

logger = logging.getLogger(__name__)


class BaseResource(Resource):
    db_model: db.Model
    request_validation_schema = {}

    def request_validation(self, request_data: dict) -> None:
        v = MyValidator(schema=self.request_validation_schema)

        if not v.validate(request_data):
            raise UnprocessableEntity(v.errors)

    def get_request_query_fields(self, request_data: dict) -> tuple:
        return get_request_query_fields(self.db_model, request_data)

    def create_search_query(self, query: ModelSelect, request_data: dict) -> ModelSelect:
        return create_search_query(self.db_model, query, request_data)


@api.resource('')
class WelcomeResource(Resource):
    def get(self) -> tuple:
        return 'Welcome to flask_api!', 200


@api.resource('routes')
class RoutesResource(Resource):
    def get(self) -> tuple:
        routes = {}

        for route in current_app.url_map.iter_rules():
            if route.rule == '/static/<path:filename>':
                continue

            if route.endpoint.find('.') != -1:
                url_prefix = route.endpoint.split('.')[0]
            else:
                url_prefix = '/'

            if not url_prefix in routes.keys():
                routes[url_prefix] = []

            routes.get(url_prefix).append({
                'route': route.rule,
                'methods': list(route.methods),
            })
            routes[url_prefix] = sorted(routes.get(url_prefix), key=itemgetter('route'))

        routes = collections.OrderedDict(sorted(routes.items()))

        return {
                   'routes': routes,
               }, 200
