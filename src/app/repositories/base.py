from datetime import datetime, UTC

from flask_sqlalchemy.model import DefaultMeta

from app.extensions import db
from app.helpers.sqlalchemy_query_builder import SQLAlchemyQueryBuilder


class BaseRepository:
    def __init__(self, model: type[DefaultMeta]):
        self.model = model

    def create(self, **kwargs) -> db.Model:
        return self.model(**kwargs)

    def delete(self, record_id: int, force_delete: bool = False) -> db.Model:
        record = self.find_by_id(record_id)

        if force_delete:
            raise NotImplementedError
        else:
            record.deleted_at = datetime.now(UTC)

        return record

    def find(self, *args, **kwargs) -> db.Model | None:
        query = db.session.query(self.model)

        if args:
            query = query.filter(*args)

        if kwargs:
            query = query.filter_by(**kwargs)

        return query.first()

    def find_by_id(self, record_id: int, *args, **kwargs) -> db.Model | None:
        args += (self.model.id == record_id,)
        return self.find(*args, **kwargs)

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

    def save(self, record_id: int, **kwargs) -> db.Model:
        record = self.find_by_id(record_id)

        for key, value in kwargs.items():
            setattr(record, key, value)

        return record
