import json

from flask_restful import Api, Resource
from flask import Blueprint, request
from playhouse.shortcuts import model_to_dict

from ..models.person import Person as PersonModel

blueprint = Blueprint('person', __name__, url_prefix='/person')
api = Api(blueprint)


@api.resource('')
class NewPersonResource(Resource):
    def post(self):
        data = dict(request.get_json())

        person = PersonModel(**data).save()

        return {
            'data': person
        }

@api.resource('/<int:person_id>')
class PersonResource(Resource):
    def put(self, person_id):
        data = dict(request.get_json())

        data['id'] = person_id
        person = PersonModel(**data).save()

        person = PersonModel.get(person_id)

        return {
            'data': model_to_dict(person)
        }

    def delete(self, person_id):
        q = PersonModel.delete().where(PersonModel.id == person_id).execute()

        return {}
