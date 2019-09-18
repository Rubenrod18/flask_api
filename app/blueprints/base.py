# Related third party imports
from flask_restful import Api, Resource
from flask import Blueprint


blueprint = Blueprint('base', __name__, url_prefix='/')
api = Api(blueprint)

@api.resource('')
class BaseResource(Resource):
    def get(self):
        return 'Welcome to flask_api!', 200
