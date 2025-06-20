from flask import Blueprint, jsonify
from flask_marshmallow import Schema
from flask_restx import Resource

from ..extensions import api as root_api

blueprint = Blueprint('base', __name__)
api = root_api.namespace('', description='Base endpoints')


class SerializerMixin:
    serializer_class = None
    serializer_classes = {}

    def __init_subclass__(cls):
        super().__init_subclass__()
        cls._validate_serializer_classes()

    @classmethod
    def _validate_serializer_classes(cls):
        if cls.serializer_class is not None:
            if not isinstance(cls.serializer_class, type):
                raise TypeError(f'{cls.__name__}.serializer_class must be a class')
            if not issubclass(cls.serializer_class, Schema):
                raise TypeError(f'{cls.__name__}.serializer_class must inherit from marshmallow.Schema')

        if cls.serializer_classes:
            for name, serializer in cls.serializer_classes.items():
                if not isinstance(serializer, type):
                    raise TypeError(f"{cls.__name__}.serializer_classes['{name}'] must be a class")
                if not issubclass(serializer, Schema):
                    raise TypeError(f"{cls.__name__}.serializer_classes['{name}'] must inherit from marshmallow.Schema")

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
