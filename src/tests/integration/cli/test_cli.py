from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import DefaultMeta


class TestCli:
    def test_is_cli_seeder_ok_execute_all_seeders_process_executed_successfully(self, runner):
        result = runner.invoke(args=['seed'])

        stdout_str = result.stdout_bytes.decode('utf-8')
        finished_message = 'Database seeding completed successfully'
        is_finished_process = stdout_str.find(finished_message) != -1

        assert result.exit_code == 0, result.exception
        assert is_finished_process

    def test_is_flask_shell_ok_resources_are_available_returns_resources(self, app):
        resources = app.make_shell_context()

        assert isinstance(resources['app'], Flask)
        assert isinstance(resources['db'], SQLAlchemy)
        assert isinstance(resources['Document'], DefaultMeta)
        assert isinstance(resources['Role'], DefaultMeta)
        assert isinstance(resources['User'], DefaultMeta)
        assert isinstance(resources['UsersRolesThrough'], DefaultMeta)
