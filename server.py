#! /usr/bin/env python
from flask import jsonify, Flask
from flask_restful import reqparse, Resource, Api
from peewee import *
from playhouse.shortcuts import model_to_dict, dict_to_model

DATABASE = 'one_esecurity.db'
DEBUG = True

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()

ALLOWED_FIELDS = ['name', 'last_name', 'age', 'mother', 'father', 'birthplace']

for field in ALLOWED_FIELDS:
    parser.add_argument(field)

parser.add_argument('mother')
parser.add_argument('father')
parser.add_argument('birthplace')

sqlite_db = SqliteDatabase(DATABASE, pragmas={'journal_mode': 'wal'})

class BaseModel(Model):
    class Meta:
        database = sqlite_db

class Person(BaseModel):
    name = CharField()
    last_name = CharField()
    age = IntegerField()
    mother = CharField()
    father = CharField()
    birthplace = CharField()

MODELS = [Person]
sqlite_db.create_tables(MODELS)

class PeopleResource(Resource):
    def get(self):
        people = Person.select().paginate(1, 10)

        people_list = [model_to_dict(t, backrefs=True) for t in people]

        return {
                'data': people_list
            }

    def post(self):
        args = parser.parse_args()

        person = Person.create(**args)

        return {
                'data': model_to_dict(person)
            }

class PersonResource(Resource):
    def put(self, person_id):
        args = parser.parse_args()

        q = (Person
            .update(**args)
            .where(Person.id == person_id)
            .execute())

        person = Person.get(person_id)

        return {
                'data': model_to_dict(person)
            }

    def delete(self, person_id):
        q = Person.delete().where(Person.id == person_id).execute()

        return {}

api.add_resource(PeopleResource, '/people')
api.add_resource(PersonResource, '/person/<int:person_id>')

if __name__ == '__main__':
    app.run(debug=DEBUG)
