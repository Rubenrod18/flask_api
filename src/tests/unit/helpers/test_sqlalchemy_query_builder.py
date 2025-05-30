from datetime import datetime, UTC

import sqlalchemy as sa
from freezegun import freeze_time
from sqlalchemy.orm import Query

import app.helpers.sqlalchemy_query_builder as rqo
from app.database.factories.document_factory import DocumentFactory
from app.database.factories.role_factory import RoleFactory
from app.database.factories.user_factory import UserFactory
from app.extensions import db
from app.models import Document, Role, User
from tests.base.base_test import TestBase


class _TestBaseCreateSearchQuery:
    @staticmethod
    def _search_request(
        field_name: str | list[str],
        field_op: str | list[str],
        field_value: str | list[str],
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


class TestOrderByClauseBuilder(TestBase):
    def test_ordering_asc_and_desc(self):
        doc = DocumentFactory(name='Invoice 2024-01')
        doc_2 = DocumentFactory(name='Employee Contract John Doe')

        test_cases = [
            ('asc', 'name', doc_2.name),
            ('desc', 'name', doc.name),
        ]

        for sorting, field_name, expected_record in test_cases:
            with self.subTest(msg=sorting):
                order = rqo.OrderByClauseBuilder.build_order_by(
                    Document, request_data={'order': [{'sorting': sorting, 'field_name': field_name}]}
                )
                query = db.session.query(Document).order_by(*order)

                self.assertEqual(query.first().name, expected_record)

    def test_ordering_with_more_than_one_criteria(self):
        with freeze_time('2020-01-01'):
            doc = DocumentFactory(name='Invoice 2024-01')

        with freeze_time('2015-01-01'):
            doc_2 = DocumentFactory(name='Employee Contract John Doe')

        test_cases = [
            ([{'sorting': 'asc', 'field_name': 'name'}, {'sorting': 'desc', 'field_name': 'created_at'}], doc_2.name),
            ([{'sorting': 'desc', 'field_name': 'name'}, {'sorting': 'asc', 'field_name': 'created_at'}], doc.name),
        ]

        for sorting, expected_record in test_cases:
            with self.subTest(msg=sorting):
                order = rqo.OrderByClauseBuilder.build_order_by(Document, request_data={'order': sorting})
                query = db.session.query(Document).order_by(*order)

                self.assertEqual(query.first().name, expected_record)


class TestStringQueryClauseBuilder(TestBase):
    def setUp(self):
        super().setUp()
        self.string_clause_helper = rqo.StringQueryClauseBuilder()

    def test_create_search_query_str(self):
        user = UserFactory(name='Alice', last_name='Johnson')
        user_2 = UserFactory(name='John', last_name='Smith')
        user_3 = UserFactory(name='Michael', last_name='Williams')

        test_cases = (
            ('equals', (User.name, rqo.EQUAL_OP, user.name), User.name == user.name, None),
            ('not equals', (User.name, rqo.NOT_EQUAL_OP, user_2.name), User.name != user_2.name, None),
            ('contains', (User.name, rqo.CONTAINS_OP, user_3.name), User.name.like(f'%{user_3.name}%'), None),
            ('not contains', (User.name, rqo.NOT_CONTAINS_OP, user_3.name), ~User.name.like(f'%{user_3.name}%'), None),
            ('starts with', (User.name, rqo.STARTS_WITH_OP, user_2.name), User.name.like(f'{user_2.name}%'), None),
            ('ends with', (User.name, rqo.ENDS_WITH_OP, user_2.name), User.name.like(f'%{user_2.name}'), None),
            (
                'multiple values',
                (User.name, rqo.ENDS_WITH_OP, f'{user_2.name}{rqo.REQUEST_QUERY_DELIMITER}{user_3.name}'),
                sa.or_(*(User.name.like(f'%{user_2.name}'), User.name.like(f'%{user_3.name}'))),
                (f'%{user_2.name}', f'%{user_3.name}'),
            ),
        )

        for str_operator, test_case, expected, expected_clauses in test_cases:
            field, field_operator, field_value = test_case
            with self.subTest(msg=str_operator):
                sql_clause = self.string_clause_helper.build_clause_with_multiple_values(
                    field, field_operator, field_value
                )
                self.assertEqual(sql_clause.operator, expected.operator)
                if str_operator == 'multiple values':
                    for index, _ in enumerate(sql_clause.clauses):
                        self.assertEqual(
                            sql_clause.clauses[index].right.value, expected_clauses[index], msg=str_operator
                        )
                else:
                    self.assertEqual(sql_clause.right.value, expected.right.value, msg=str_operator)


class TestComparisonClauseBuilder(TestBase):
    def setUp(self):
        super().setUp()
        self.operator_clause_helper = rqo.ComparisonClauseBuilder()

    def test_create_search_query_datetime(self):
        with freeze_time('2020-01-01'):
            doc = DocumentFactory(name='Invoice 2024-01', created_at=datetime.now(UTC))

        with freeze_time('2015-01-01'):
            doc_2 = DocumentFactory(name='Employee Contract John Doe', created_at=datetime.now(UTC))

        with freeze_time('2010-01-01'):
            doc_3 = DocumentFactory(name='Monthly Sales Report March', created_at=datetime.now(UTC))

        test_cases = (
            (
                'equal',
                (Document.created_at, rqo.EQUAL_OP, doc.created_at.strftime('%Y-%m-%d %H:%M:%S')),
                Document.created_at == doc.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                None,
            ),
            (
                'not equal',
                (Document.created_at, rqo.NOT_EQUAL_OP, doc.created_at.strftime('%Y-%m-%d %H:%M:%S')),
                Document.created_at != doc.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                None,
            ),
            (
                'less than',
                (Document.created_at, rqo.LESS_THAN_OP, doc.created_at.strftime('%Y-%m-%d %H:%M:%S')),
                Document.created_at < doc.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                None,
            ),
            (
                'less than or equal',
                (Document.created_at, rqo.LESS_THAN_OR_EQUAL_TO_OP, doc.created_at.strftime('%Y-%m-%d %H:%M:%S')),
                Document.created_at <= doc.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                None,
            ),
            (
                'great than',
                (Document.created_at, rqo.GREATER_THAN_OP, doc_3.created_at.strftime('%Y-%m-%d %H:%M:%S')),
                Document.created_at > doc_3.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                None,
            ),
            (
                'great than or equal',
                (Document.created_at, rqo.GREATER_THAN_OR_EQUAL_TO_OP, doc_3.created_at.strftime('%Y-%m-%d %H:%M:%S')),
                Document.created_at >= doc_3.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                None,
            ),
            (
                'between',
                (
                    Document.created_at,
                    rqo.BETWEEN_OP,
                    (
                        f'{doc_2.created_at.strftime("%Y-%m-%d %H:%M:%S")}'
                        f'{rqo.REQUEST_QUERY_DELIMITER}'
                        f'{doc_3.created_at.strftime("%Y-%m-%d %H:%M:%S")}'
                    ),
                ),
                Document.created_at.between(doc_2.created_at, doc_3.created_at),
                (doc_2.created_at.strftime('%Y-%m-%d %H:%M:%S'), doc_3.created_at.strftime('%Y-%m-%d %H:%M:%S')),
            ),
            (
                'multiple values',
                (
                    Document.created_at,
                    rqo.GREATER_THAN_OP,
                    (
                        f'{doc_3.created_at.strftime("%Y-%m-%d %H:%M:%S")}'
                        f'{rqo.REQUEST_QUERY_DELIMITER}'
                        f'{doc.created_at.strftime("%Y-%m-%d %H:%M:%S")}'
                    ),
                ),
                sa.or_(
                    *(
                        Document.created_at > doc_3.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        Document.created_at > doc.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    )
                ),
                (doc_3.created_at.strftime('%Y-%m-%d %H:%M:%S'), doc.created_at.strftime('%Y-%m-%d %H:%M:%S')),
            ),
        )

        for str_operator, test_case, expected, expected_clauses in test_cases:
            field, field_operator, field_value = test_case
            with self.subTest(msg=str_operator):
                sql_clause = self.operator_clause_helper.build_clause_with_multiple_values(
                    field, field_operator, field_value
                )
                self.assertEqual(sql_clause.operator, expected.operator)
                if str_operator == 'multiple values':
                    for index, _ in enumerate(sql_clause.clauses):
                        self.assertEqual(
                            sql_clause.clauses[index].right.value, expected_clauses[index], msg=str_operator
                        )
                elif str_operator == 'between':
                    for index, _ in enumerate(sql_clause.right.clauses):
                        self.assertEqual(
                            sql_clause.right.clauses[index].value, expected_clauses[index], msg=str_operator
                        )
                else:
                    self.assertEqual(sql_clause.right.value, expected.right.value, msg=str_operator)

    def test_create_search_query_integer(self):
        doc = DocumentFactory(name='Invoice 2024-01', size=1_000_000)
        doc_2 = DocumentFactory(name='Employee Contract John Doe', size=2_000_000)
        doc_3 = DocumentFactory(name='Monthly Sales Report March', size=3_000_000)

        test_cases = (
            (
                'equals',
                (Document.size, rqo.EQUAL_OP, doc.size),
                Document.size == doc.size,
                None,
            ),
            (
                'not equals',
                (Document.size, rqo.NOT_EQUAL_OP, doc.size),
                Document.size != doc.size,
                None,
            ),
            (
                'less than',
                (Document.size, rqo.LESS_THAN_OP, doc_2.size),
                Document.size < doc_2.size,
                None,
            ),
            (
                'less than or equal',
                (Document.size, rqo.LESS_THAN_OR_EQUAL_TO_OP, doc_2.size),
                Document.size <= doc_2.size,
                None,
            ),
            (
                'great than',
                (Document.size, rqo.GREATER_THAN_OP, doc_2.size),
                Document.size > doc_2.size,
                None,
            ),
            (
                'great than or equal',
                (Document.size, rqo.GREATER_THAN_OR_EQUAL_TO_OP, doc_2.size),
                Document.size >= doc_2.size,
                None,
            ),
            (
                'in',
                (
                    Document.size,
                    rqo.IN_OP,
                    f'{doc_3.size}{rqo.REQUEST_QUERY_DELIMITER}{doc_2.size}{rqo.REQUEST_QUERY_DELIMITER}{doc.size}',
                ),
                Document.size.in_([f'{doc_3.size}', f'{doc_2.size}', f'{doc.size}']),
                None,
            ),
            (
                'not in',
                (
                    Document.size,
                    rqo.NOT_IN_OP,
                    f'{doc_3.size}{rqo.REQUEST_QUERY_DELIMITER}{doc_2.size}{rqo.REQUEST_QUERY_DELIMITER}{doc.size}',
                ),
                ~Document.size.in_([f'{doc_3.size}', f'{doc_2.size}', f'{doc.size}']),
                None,
            ),
            (
                'multiple values',
                (Document.size, rqo.GREATER_THAN_OP, f'{doc_3.size}{rqo.REQUEST_QUERY_DELIMITER}{doc.size}'),
                sa.or_(*(Document.size > doc_3.size, Document.size > doc.size)),
                (f'{doc_3.size}', f'{doc.size}'),
            ),
        )

        for str_operator, test_case, expected, expected_clauses in test_cases:
            field, field_operator, field_value = test_case
            with self.subTest(msg=str_operator):
                sql_clause = self.operator_clause_helper.build_clause_with_multiple_values(
                    field, field_operator, field_value
                )
                self.assertEqual(sql_clause.operator, expected.operator)
                if str_operator == 'multiple values':
                    for index, _ in enumerate(sql_clause.clauses):
                        self.assertEqual(
                            sql_clause.clauses[index].right.value, expected_clauses[index], msg=str_operator
                        )
                elif str_operator == 'between':
                    for index, _ in enumerate(sql_clause.right.clauses):
                        self.assertEqual(
                            sql_clause.right.clauses[index].value, expected_clauses[index], msg=str_operator
                        )
                else:
                    self.assertEqual(sql_clause.right.value, expected.right.value, msg=str_operator)


class TestSQLAlchemyQueryBuilderStrings(TestBase, _TestBaseCreateSearchQuery):
    def setUp(self):
        super().setUp()
        self.query_helper = rqo.QueryClauseBuilder()
        self.ordering_helper = rqo.OrderByClauseBuilder()
        self.rqo = rqo.SQLAlchemyQueryBuilder(self.query_helper, self.ordering_helper)

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
                query = self.rqo.create_search_query(User, db.session.query(User.id), test_case)
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
                query = self.rqo.create_search_query(Role, db.session.query(Role.id), test_case)
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
                query = self.rqo.create_search_query(User, db.session.query(User.id), test_case)
                self.assertEqual(self._get_values(query), expected, msg=str_operator)


class TestSQLAlchemyQueryBuilderNoStrings(TestBase, _TestBaseCreateSearchQuery):
    def setUp(self):
        super().setUp()
        self.query_helper = rqo.QueryClauseBuilder()
        self.ordering_helper = rqo.OrderByClauseBuilder()
        self.rqo = rqo.SQLAlchemyQueryBuilder(self.query_helper, self.ordering_helper)

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
                        f'{rqo.REQUEST_QUERY_DELIMITER}'
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
                query = self.rqo.create_search_query(Document, db.session.query(Document.id), test_case)
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
                        f'{rqo.REQUEST_QUERY_DELIMITER}'
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
                query = self.rqo.create_search_query(User, db.session.query(User.id), test_case)
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
                    field_value=(
                        f'{doc_3.size}{rqo.REQUEST_QUERY_DELIMITER}{doc_2.size}{rqo.REQUEST_QUERY_DELIMITER}{doc.size}'
                    ),
                ),
                {doc.id, doc_2.id, doc_3.id},
            ),
            (
                'nin',
                self._search_request(
                    field_name='size',
                    field_op='nin',
                    field_value=f'{doc_3.size}{rqo.REQUEST_QUERY_DELIMITER}{doc_2.size}',
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
                query = self.rqo.create_search_query(Document, db.session.query(Document.id), test_case)
                self.assertEqual(self._get_values(query), expected, msg=str_operator)
