from datetime import datetime, UTC

from app.extensions import db
from app.helpers.request_query_operator import RequestQueryOperator
from app.models import Base


class BaseManager(object):
    def __init__(self, *args, **kwargs):
        self.model = Base

    def create(self, **kwargs):
        current_date = datetime.now(UTC)
        kwargs.update(
            {
                'created_at': current_date,
                'updated_at': current_date,
            }
        )

        record = self.model(**kwargs)
        return record

    def save(self, record_id: int, **kwargs):
        record = db.session.query(self.model).filter_by(id=record_id).first()

        for key, value in kwargs.items():
            setattr(record, key, value)

        return record

    def get(self, **kwargs):
        rqo = RequestQueryOperator()
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

    def delete(self, record_id: int):
        record = self.find(record_id)
        record.deleted_at = datetime.now(UTC)
        return record

    def find(self, record_id: int, *args):
        query = db.session.query(self.model).filter(self.model.id == record_id)

        for arg in args:
            query = query.filter(arg)

        return query.first()
