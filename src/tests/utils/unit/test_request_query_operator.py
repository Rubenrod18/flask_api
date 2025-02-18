import typing
from datetime import datetime, UTC

from freezegun import freeze_time
from sqlalchemy.orm import Query

from app.database.factories.document_factory import DocumentFactory
from app.database.factories.role_factory import RoleFactory
from app.database.factories.user_factory import UserFactory
from app.extensions import db
from app.models import Document, Role, User
from app.utils.request_query_operator import REQUEST_QUERY_DELIMITER, RequestQueryOperator as rqo
from tests.base.base_test import TestBase


class TestBaseCreateSearchQuery:
    @staticmethod
    def _search_request(
        field_name: typing.Union[str, list[str]],
        field_op: typing.Union[str, list[str]],
        field_value: typing.Union[str, list[str]],
    ):
        if isinstance(field_name, list) and isinstance(field_op, list) and isinstance(field_value, list):
            search_value = [
                {'field_name': field_name[i], 'field_operator': field_op[i], 'field_value': field_value[i]}
                for i in range(len(field_name))
            ]
        else:
            search_value = [{'field_name': field_name, 'field_operator': field_op, 'field_value': field_value}]

        return {'search': search_value}

    @staticmethod
    def _get_values(query: Query) -> set[int]:
        return {item[0] for item in query.all()}


class TestCreateSearchQueryStrings(TestBase, TestBaseCreateSearchQuery):
    def test_create_search_query_str(self):
        user = UserFactory(name='Alice', last_name='Johnson')
        user_2 = UserFactory(name='John', last_name='Smith')
        user_3 = UserFactory(name='Michael', last_name='Williams')

        test_cases = (
            ('equals', self._search_request('name', 'eq', 'Michael'), {user_3.id}),
            ('not equals', self._search_request('name', 'ne', 'Michael'), {user.id, user_2.id}),
            ('contains', self._search_request('name', 'contains', 'e'), {user.id, user_3.id}),
            ('not contains', self._search_request('last_name', 'ncontains', 'i'), {user.id}),
            ('starts with', self._search_request('last_name', 'startswith', 'S'), {user_2.id}),
            ('ends with', self._search_request('last_name', 'endswith', 'h'), {user_2.id}),
            (
                'multiple queries',
                (
                    self._search_request(
                        field_name=['name', 'last_name'], field_op=['contains', 'ncontains'], field_value=['a', 'o']
                    )
                ),
                {user_3.id},
            ),
        )

        for str_operator, test_case, expected in test_cases:
            with self.subTest(msg=str_operator):
                query = rqo.create_search_query(User, db.session.query(User.id), test_case)
                self.assertEqual(self._get_values(query), expected, msg=str_operator)

    def test_create_search_query_text(self):
        software_engineer_description = 'Designs, develops, and maintains software applications.'
        role = RoleFactory(name='software_engineer', description=software_engineer_description)
        role_2 = RoleFactory(name='marketing_manager', description='Develops and implements marketing strategies.')
        role_3 = RoleFactory(
            name='hr_specialist',
            description='Manages recruitment, employee relations, performance, and ensures compliance with labor laws.',
        )

        test_cases = (
            ('equals', self._search_request('description', 'eq', software_engineer_description), {role.id}),
            (
                'not equals',
                self._search_request('description', 'ne', software_engineer_description),
                {role_2.id, role_3.id},
            ),
            ('contains', self._search_request('description', 'contains', 'develops'), {role.id, role_2.id}),
            ('not contains', self._search_request('description', 'ncontains', 'develops'), {role_3.id}),
            ('starts with', self._search_request('description', 'startswith', 'D'), {role.id, role_2.id}),
            ('ends with', self._search_request('description', 'endswith', '.'), {role.id, role_2.id, role_3.id}),
            (
                'multiple queries',
                (
                    self._search_request(
                        field_name=['name', 'description'],
                        field_op=['contains', 'contains'],
                        field_value=['ing', 'develops'],
                    )
                ),
                {role_2.id},
            ),
        )

        for str_operator, test_case, expected in test_cases:
            with self.subTest(msg=str_operator):
                query = rqo.create_search_query(Role, db.session.query(Role.id), test_case)
                self.assertEqual(self._get_values(query), expected, msg=str_operator)

    def test_create_search_query_uuid(self):
        user = UserFactory()
        user_2 = UserFactory()
        user_3 = UserFactory()

        test_cases = (
            ('equals', self._search_request('fs_uniquifier', 'eq', user.fs_uniquifier), {user.id}),
            ('not equals', self._search_request('fs_uniquifier', 'ne', user.fs_uniquifier), {user_2.id, user_3.id}),
        )

        for str_operator, test_case, expected in test_cases:
            with self.subTest(msg=str_operator):
                query = rqo.create_search_query(User, db.session.query(User.id), test_case)
                self.assertEqual(self._get_values(query), expected, msg=str_operator)


class TestCreateSearchQueryNoStrings(TestBase, TestBaseCreateSearchQuery):
    def test_create_search_query_datetime(self):
        with freeze_time('2020-01-01'):
            doc = DocumentFactory(name='Invoice 2024-01', created_at=datetime.now(UTC))

        with freeze_time('2015-01-01'):
            doc_2 = DocumentFactory(name='Employee Contract John Doe', created_at=datetime.now(UTC))

        with freeze_time('2010-01-01'):
            doc_3 = DocumentFactory(name='Monthly Sales Report March', created_at=datetime.now(UTC))

        test_cases = (
            (
                'equals',
                self._search_request('created_at', 'eq', doc.created_at.strftime('%Y-%m-%d %H:%M:%S')),
                {doc.id},
            ),
            (
                'not equals',
                self._search_request('created_at', 'ne', doc.created_at.strftime('%Y-%m-%d %H:%M:%S')),
                {doc_2.id, doc_3.id},
            ),
            (
                'less than',
                self._search_request('created_at', 'lt', doc.created_at.strftime('%Y-%m-%d %H:%M:%S')),
                {doc_2.id, doc_3.id},
            ),
            (
                'less than equals',
                self._search_request('created_at', 'lte', doc.created_at.strftime('%Y-%m-%d %H:%M:%S')),
                {doc.id, doc_2.id, doc_3.id},
            ),
            (
                'great than',
                self._search_request('created_at', 'gt', doc_3.created_at.strftime('%Y-%m-%d %H:%M:%S')),
                {doc.id, doc_2.id},
            ),
            (
                'great than equals',
                self._search_request('created_at', 'gte', doc_3.created_at.strftime('%Y-%m-%d %H:%M:%S')),
                {doc.id, doc_2.id, doc_3.id},
            ),
            (
                'between',
                self._search_request(
                    field_name='created_at',
                    field_op='between',
                    field_value=(
                        f'{doc_3.created_at.strftime("%Y-%m-%d %H:%M:%S")}'
                        f'{REQUEST_QUERY_DELIMITER}'
                        f'{doc_2.created_at.strftime("%Y-%m-%d %H:%M:%S")}'
                    ),
                ),
                {doc_2.id, doc_3.id},
            ),
            (
                'multiple queries',
                (
                    self._search_request(
                        field_name=['created_at', 'created_at'],
                        field_op=['gt', 'gte'],
                        field_value=[
                            doc_3.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                            doc.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        ],
                    )
                ),
                {doc.id},
            ),
        )

        for str_operator, test_case, expected in test_cases:
            with self.subTest(msg=str_operator):
                query = rqo.create_search_query(Document, db.session.query(Document.id), test_case)
                self.assertEqual(self._get_values(query), expected, msg=str_operator)

    def test_create_search_query_date(self):
        with freeze_time('2020-01-01'):
            user = UserFactory(birth_date=datetime.now(UTC))

        with freeze_time('2015-01-01'):
            user_2 = UserFactory(birth_date=datetime.now(UTC))

        with freeze_time('2010-01-01'):
            user_3 = UserFactory(birth_date=datetime.now(UTC))

        test_cases = (
            ('equals', self._search_request('birth_date', 'eq', user.birth_date.strftime('%Y-%m-%d')), {user.id}),
            (
                'not equals',
                self._search_request('birth_date', 'ne', user.birth_date.strftime('%Y-%m-%d')),
                {user_2.id, user_3.id},
            ),
            (
                'less than',
                self._search_request('birth_date', 'lt', user.birth_date.strftime('%Y-%m-%d')),
                {user_2.id, user_3.id},
            ),
            (
                'less than equals',
                self._search_request('birth_date', 'lte', user.birth_date.strftime('%Y-%m-%d')),
                {user.id, user_2.id, user_3.id},
            ),
            (
                'great than',
                self._search_request('birth_date', 'gt', user_3.birth_date.strftime('%Y-%m-%d')),
                {user.id, user_2.id},
            ),
            (
                'great than equals',
                self._search_request('birth_date', 'gte', user_3.birth_date.strftime('%Y-%m-%d')),
                {user.id, user_2.id, user_3.id},
            ),
            (
                'between',
                self._search_request(
                    field_name='birth_date',
                    field_op='between',
                    field_value=(
                        f'{user_3.birth_date.strftime("%Y-%m-%d")}'
                        f'{REQUEST_QUERY_DELIMITER}'
                        f'{user_2.birth_date.strftime("%Y-%m-%d")}'
                    ),
                ),
                {user_2.id, user_3.id},
            ),
            (
                'multiple queries',
                (
                    self._search_request(
                        field_name=['birth_date', 'birth_date'],
                        field_op=['gt', 'gte'],
                        field_value=[user_3.birth_date.strftime('%Y-%m-%d'), user.birth_date.strftime('%Y-%m-%d')],
                    )
                ),
                {user.id},
            ),
        )

        for str_operator, test_case, expected in test_cases:
            with self.subTest(msg=str_operator):
                query = rqo.create_search_query(User, db.session.query(User.id), test_case)
                self.assertEqual(self._get_values(query), expected, msg=str_operator)

    def test_create_search_query_integer(self):
        doc = DocumentFactory(name='Invoice 2024-01', size=1_000_000)
        doc_2 = DocumentFactory(name='Employee Contract John Doe', size=2_000_000)
        doc_3 = DocumentFactory(name='Monthly Sales Report March', size=3_000_000)

        test_cases = (
            ('equals', self._search_request('size', 'eq', doc.size), {doc.id}),
            ('not equals', self._search_request('size', 'ne', doc.size), {doc_2.id, doc_3.id}),
            ('less than', self._search_request('size', 'lt', doc_2.size), {doc.id}),
            ('less than equals', self._search_request('size', 'lte', doc_2.size), {doc.id, doc_2.id}),
            ('great than', self._search_request('size', 'gt', doc_2.size), {doc_3.id}),
            ('great than equals', self._search_request('size', 'gte', doc_2.size), {doc_2.id, doc_3.id}),
            (
                'in',
                self._search_request(
                    field_name='size',
                    field_op='in',
                    field_value=f'{doc_3.size}{REQUEST_QUERY_DELIMITER}{doc_2.size}{REQUEST_QUERY_DELIMITER}{doc.size}',
                ),
                {doc.id, doc_2.id, doc_3.id},
            ),
            (
                'nin',
                self._search_request(
                    field_name='size', field_op='nin', field_value=f'{doc_3.size}{REQUEST_QUERY_DELIMITER}{doc_2.size}'
                ),
                {doc.id},
            ),
            (
                'multiple queries',
                (
                    self._search_request(
                        field_name=['size', 'size'], field_op=['gt', 'gte'], field_value=[doc.size, doc_3.size + 1]
                    )
                ),
                set(),
            ),
        )

        for str_operator, test_case, expected in test_cases:
            with self.subTest(msg=str_operator):
                query = rqo.create_search_query(Document, db.session.query(Document.id), test_case)
                self.assertEqual(self._get_values(query), expected, msg=str_operator)
