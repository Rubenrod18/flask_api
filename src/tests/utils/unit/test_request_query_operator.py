from app.database.factories.user_factory import UserFactory
from app.extensions import db
from app.models import User
from app.utils.request_query_operator import RequestQueryOperator as rqo
from tests.base.base_test import TestBase


class TestCreateSearchQueryStrings(TestBase):
    def setUp(self):
        super(TestCreateSearchQueryStrings, self).setUp()
        # TODO: pending to define tests of ne, contains, ncontains, startswith, endswith

    def test_create_search_query_str(self):
        user = UserFactory()
        kwargs = {'search': [{'field_name': 'name', 'field_operator': 'eq', 'field_value': user.name}]}

        query = db.session.query(User)
        query = rqo.create_search_query(User, query, kwargs)

        self.assertEqual(query.count(), 1)
