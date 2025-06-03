import os
from datetime import datetime, UTC
from unittest.mock import patch, PropertyMock

from flask_sqlalchemy.model import DefaultMeta
from flask_sqlalchemy.query import Query

from app.database.factories.user_factory import UserFactory
from app.extensions import db
from app.helpers.sqlalchemy_query_builder import EQUAL_OP
from app.managers import UserManager
from app.models import User
from app.models.user import Genre
from tests.base.base_test import BaseTest


class UserManagerTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.manager = UserManager()

    def test_check_manager_property(self):
        with patch.object(UserManager, 'model', new_callable=PropertyMock) as mock_value:
            mock_value.return_value = User
            user_manager = UserManager()
            self.assertEqual(type(user_manager.model), DefaultMeta)

    def test_create_user(self):
        with self.assertRaises(NotImplementedError):
            self.manager.create(**{})

    @patch('app.managers.user.UserRepository.find', autospec=True)
    def test_save_user(self, mock_repo_find):
        user = UserFactory(active=True, deleted_at=None)
        user_data = UserFactory.build_dict(
            exclude={'created_by', 'roles', 'fs_uniquifier', 'created_at', 'updated_at', 'deleted_at'}
        )
        user_data['password'] = os.getenv('TEST_USER_PASSWORD')
        mock_repo_find.return_value = db.session.get(User, user.id)

        user = self.manager.save(user.id, **user_data)

        mock_repo_find.assert_called_once()
        self.assertEqual(user.name, user_data['name'])
        self.assertEqual(user.last_name, user_data['last_name'])
        self.assertEqual(user.email, user_data['email'])
        self.assertEqual(user.password, user_data['password'])
        self.assertIn(user.genre, Genre.to_list())
        self.assertIn(user.active, [True, False])
        self.assertIsNone(user.created_by_user)
        self.assertTrue(isinstance(user.created_at, datetime))
        self.assertTrue(isinstance(user.updated_at, datetime))
        self.assertIsNone(user.deleted_at)
        self.assertIsNotNone(db.session.get(User, user.id))
        self.assertTrue(db.session.query(User.id).filter(User.id != user.id).first() is None)

    @patch('app.managers.base.SQLAlchemyQueryBuilder.get_request_query_fields', autospec=True)
    @patch('app.managers.base.SQLAlchemyQueryBuilder.create_search_query', autospec=True)
    def test_get_users_no_filter_criteria(self, mock_create_search_query, mock_get_request_query_fields):
        mock_create_search_query.return_value = db.session.query(User)
        mock_get_request_query_fields.return_value = 0, 10, []
        UserFactory.create_batch(5)

        all_users = self.manager.get()

        mock_get_request_query_fields.assert_called_once()
        mock_create_search_query.assert_called_once()
        self.assertTrue(isinstance(all_users['query'], Query))
        self.assertTrue(all(isinstance(doc, User) for doc in all_users['query']))
        self.assertEqual(all_users['records_filtered'], 5)
        self.assertEqual(all_users['records_total'], 5)

    @patch('app.managers.base.SQLAlchemyQueryBuilder.get_request_query_fields', autospec=True)
    @patch('app.managers.base.SQLAlchemyQueryBuilder.create_search_query', autospec=True)
    def test_get_users_with_filter_criteria(self, mock_create_search_query, mock_get_request_query_fields):
        created_users = UserFactory.create_batch(5)
        mock_create_search_query.return_value = db.session.query(User).where(User.name == created_users[0].name)
        mock_get_request_query_fields.return_value = 0, 10, []

        filtered_users = self.manager.get(
            **{
                'items_per_page': 10,
                'order': [],
                'page_number': 1,
                'search': [
                    {
                        'field_name': 'name',
                        'field_operator': EQUAL_OP,
                        'field_value': created_users[0].name,
                    }
                ],
            }
        )

        self.assertTrue(isinstance(filtered_users['query'], Query))
        self.assertTrue(all(isinstance(doc, User) for doc in filtered_users['query']))
        self.assertEqual(filtered_users['records_filtered'], 1)
        self.assertEqual(filtered_users['records_total'], 5)

    @patch('app.managers.user.UserRepository.delete', autospec=True)
    def test_delete_soft_user(self, mock_repo_delete):
        user = UserFactory()
        user = UserFactory(created_by_user=user, deleted_at=None)

        def fake_delete(self, doc, force_delete=False):  # noqa  # pylint: disable=unused-argument
            doc.deleted_at = datetime.now(UTC)
            return doc

        mock_repo_delete.side_effect = fake_delete

        deleted_user = self.manager.delete(user.id)

        mock_repo_delete.assert_called_once()
        self.assertTrue(isinstance(deleted_user, User))
        self.assertEqual(deleted_user.id, user.id)
        self.assertTrue(isinstance(deleted_user.deleted_at, datetime))

    @patch('app.managers.user.UserRepository.find', autospec=True)
    def test_find_by_id_user(self, mock_repo_find):
        user = UserFactory(created_by_user=UserFactory(), deleted_at=None)
        mock_repo_find.return_value = db.session.get(User, user.id)

        found_user = self.manager.find_by_id(user.id)

        mock_repo_find.assert_called_once()
        self.assertTrue(isinstance(found_user, User))
        self.assertEqual(found_user.id, user.id)

    @patch('app.managers.user.UserRepository.find', autospec=True)
    def test_find_by_email(self, mock_repo_find):
        user = UserFactory(created_by_user=UserFactory(), deleted_at=None)
        mock_repo_find.return_value = db.session.get(User, user.id)

        found_user = self.manager.find_by_email(user.email)

        mock_repo_find.assert_called_once()
        self.assertTrue(isinstance(found_user, User))
        self.assertEqual(found_user.email, user.email)

    def test_get_last_record(self):
        users = UserFactory.create_batch(3)

        with patch('app.managers.user.db.session.query') as mock_query:
            mock_query.return_value.order_by.return_value.limit.return_value.first.return_value = users[-1]
            found_user = self.manager.get_last_record()

            self.assertTrue(isinstance(found_user, User))
            self.assertEqual(found_user.id, 3)
