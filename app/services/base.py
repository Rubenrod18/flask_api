from marshmallow import ValidationError
from werkzeug.exceptions import UnprocessableEntity

from app.managers import BaseManager
from app.serializers import SearchSerializer


class BaseService(object):

    def __init__(self, *args, **kwargs):
        self.manager = BaseManager()

    def create(self, **kwargs):
        pass

    def save(self, **kwargs):
        pass

    def get(self, **kwargs):
        try:
            data = SearchSerializer().load(**kwargs)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        return self.manager.get(**data)

    def delete(self, record_id: int):
        pass

    def find(self, record_id: int):
        pass

