from flask import Blueprint, jsonify
from flask_restx import Resource

from ..extensions import api as root_api

blueprint = Blueprint('base', __name__)
api = root_api.namespace('', description='Base endpoints')


class BaseResource(Resource):
    serializer_class = None

    def __init__(self, rest_api: str, service, *args, **kwargs):
        super().__init__(rest_api, *args, **kwargs)
        self.service = service

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        return self.serializer_class


@api.route('/welcome')
class WelcomeResource(Resource):
    @api.doc(responses={200: 'Welcome to flask_api!'})
    def get(self) -> tuple:
        return 'Welcome to flask_api!', 200


@blueprint.route('/swagger.json')
def swagger_spec():
    schema = root_api.__schema__
    return jsonify(schema)
