from flask import Blueprint, jsonify
from flask_restx import Resource

from ..extensions import api as root_api

blueprint = Blueprint('base', __name__)
api = root_api.namespace('', description='Base endpoints')


class SerializerMixin:
    serializer_class = None
    serializer_classes = {}

    def get_serializer(self, *args, serializer_name=None, **kwargs):
        serializer_class = self.get_serializer_class(serializer_name)
        if serializer_class:
            return serializer_class(*args, **kwargs)
        raise ValueError(f"Serializer '{serializer_name}' not found in {self.__class__.__name__}")

    def get_serializer_class(self, serializer_name=None):
        if self.serializer_classes and serializer_name:
            return self.serializer_classes.get(serializer_name)
        return self.serializer_class


class BaseResource(Resource, SerializerMixin):
    def __init__(self, rest_api: str, service, *args, **kwargs):
        super().__init__(rest_api, *args, **kwargs)
        self.service = service


@api.route('/welcome')
class WelcomeResource(Resource):
    @api.doc(responses={200: 'Welcome to flask_api!'})
    def get(self) -> tuple:
        return 'Welcome to flask_api!', 200


@blueprint.route('/swagger.json')
def swagger_spec():
    schema = root_api.__schema__
    return jsonify(schema)
