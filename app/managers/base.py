from datetime import datetime

from app.utils import get_request_query_fields, create_search_query


class BaseManager(object):

    def __init__(self, *args, **kwargs):
        self.model = None

    def create(self, **kwargs):
        return self.model.create(**kwargs)

    def save(self, record_id: int, **kwargs):
        kwargs['id'] = record_id
        return self.model(**kwargs).save()

    def get(self, **kwargs):
        page, items, order = get_request_query_fields(self.model, kwargs)

        query = self.model.select()
        records_total = query.count()

        query = create_search_query(self.model, query, kwargs)
        query = query.order_by(*order).paginate(page, items)

        return {
            'query': query,
            'records_total': records_total,
            'records_filtered': query.count(),
        }

    def delete(self, record_id: int):
        record = self.find(record_id)
        record.deleted_at = datetime.utcnow()
        record.save()
        return record

    def find(self, record_id: int, *args):
        query = (self.model.id == record_id,)

        if args:
            query = query + args

        return self.model.get_or_none(*query)
