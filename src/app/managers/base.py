from datetime import datetime, UTC

from flask_sqlalchemy.model import DefaultMeta

from app.extensions import db
from app.helpers.sqlalchemy_query_builder import SQLAlchemyQueryBuilder


class BaseManager:
    def __init__(self, model: type[DefaultMeta]):
        self.model = model

    def create(self, **kwargs) -> db.Model:
        return self.model(**kwargs)

    def save(self, record_id: int, **kwargs) -> db.Model:
        record = db.session.query(self.model).filter_by(id=record_id).first()

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
            'records_total': records_total,
            'records_filtered': query.count(),
        }

    def delete(self, record_id: int) -> db.Model:
        record = self.find(record_id)
        record.deleted_at = datetime.now(UTC)
        return record

    def find(self, record_id: int, *args) -> db.Model | None:
        query = db.session.query(self.model).filter(self.model.id == record_id)

        for arg in args:
            query = query.filter(arg)

        return query.first()
