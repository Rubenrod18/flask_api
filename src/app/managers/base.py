from app.extensions import db
from app.helpers.sqlalchemy_query_builder import SQLAlchemyQueryBuilder
from app.repositories.base import BaseRepository


class BaseManager:
    def __init__(self, repository: type[BaseRepository]):
        self.repository = repository()

    @property
    def model(self):
        return self.repository.model

    def create(self, **kwargs) -> db.Model:
        return self.repository.create(**kwargs)

    def save(self, record_id: int, **kwargs) -> db.Model:
        record = self.find_by_id(record_id)

        for key, value in kwargs.items():
            setattr(record, key, value)

        return record

    def get(self, **kwargs) -> dict:
        rqo = SQLAlchemyQueryBuilder()
        page, items_per_page, order = rqo.get_request_query_fields(self.model, kwargs)

        query = db.session.query(self.model)
        records_total = db.session.query(self.model).count()

        query = rqo.create_search_query(self.model, query, kwargs)
        query = query.order_by(*order).offset(page * items_per_page).limit(items_per_page)

        return {
            'query': query,
            'records_filtered': query.count(),
            'records_total': records_total,
        }

    def delete(self, record_id: int) -> db.Model:
        record = self.find_by_id(record_id)
        return self.repository.delete(record)

    def find_by_id(self, record_id: int, *args, **kwargs) -> db.Model | None:
        args += (self.model.id == record_id,)
        return self.repository.find(*args, **kwargs)
