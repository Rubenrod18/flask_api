from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import DefaultMeta

from tests.base.base_test import TestBase


class TestCli(TestBase):
    def test_is_cli_seeder_ok_execute_all_seeders_process_executed_successfully(  # noqa
        self,
    ):
        result = self.runner.invoke(args=['seed'])

        stdout_str = result.stdout_bytes.decode('utf-8')
        finished_message = 'Database seeding completed successfully'
        is_finished_process = stdout_str.find(finished_message) != -1

        self.assertEqual(0, result.exit_code, result.exception)
        self.assertEqual(True, is_finished_process)

    def test_is_flask_shell_ok_resources_are_available_returns_resources(self):
        resources = self.app.make_shell_context()

        self.assertTrue(isinstance(resources['app'], Flask))
        self.assertTrue(isinstance(resources['db'], SQLAlchemy))
        self.assertTrue(isinstance(resources['Document'], DefaultMeta))
        self.assertTrue(isinstance(resources['Role'], DefaultMeta))
        self.assertTrue(isinstance(resources['User'], DefaultMeta))
        self.assertTrue(isinstance(resources['UsersRolesThrough'], DefaultMeta))
