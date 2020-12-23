from marshmallow import ValidationError
from werkzeug.exceptions import UnprocessableEntity

from app.managers import BaseManager
from app.serializers import SearchSerializer


class BaseService(object):

    def __init__(self, *args, **kwargs):
        self.manager = BaseManager()

    def create(self, **kwargs):
        return self.manager.create(**kwargs)

    def find(self, record_id: int, *args):
        return self.manager.find(record_id, *args)

    def save(self, record_id: int, **kwargs):
        self.manager.save(record_id, **kwargs)

        args = (self.manager.model.deleted_at.is_null(),)
        return self.manager.find(record_id, *args)

    def get(self, **kwargs):
        try:
            data = SearchSerializer().load(kwargs)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        return self.manager.get(**data)

    def delete(self, record_id: int):
        return self.manager.delete(record_id)
