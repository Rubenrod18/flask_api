from app.extensions import db
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

        args = (self.manager.model.deleted_at.is_(None),)
        return self.manager.find(record_id, *args)

    def get(self, **kwargs):
        data = SearchSerializer().load(kwargs)
        return self.manager.get(**data)

    def delete(self, record_id: int):
        return self.manager.delete(record_id)

    @property
    def is_transaction_active(self):
        # TODO: This property is temporal until I migrate the factories and seeders to SQLALchemy.
        conn = db.session.connection(execution_options={"isolation_level": "AUTOCOMMIT"})
        return conn.get_transaction() is not None
