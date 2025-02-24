from flask import Blueprint, jsonify
from flask_restx import Resource

from ..extensions import api as root_api

blueprint = Blueprint('base', __name__)
api = root_api.namespace('', description='Base endpoints')


@api.route('/welcome')
class WelcomeResource(Resource):
    @api.doc(responses={200: 'Welcome to flask_api!'})
    def get(self) -> tuple:
        return 'Welcome to flask_api!', 200


@blueprint.route('/swagger.json')
def swagger_spec():
    schema = root_api.__schema__
    return jsonify(schema)
