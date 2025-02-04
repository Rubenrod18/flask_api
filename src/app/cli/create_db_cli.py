from abc import ABC

from flask import current_app
from sqlalchemy import create_engine, text

from app.cli._base_cli import _BaseCli


class CreateDatabaseCli(_BaseCli, ABC):
    def run_command(self):
        uri = current_app.config['SQLALCHEMY_DATABASE_URI']
        base_uri, dbname = uri.rsplit('/', 1)
        engine = create_engine(base_uri)

        with engine.connect() as conn:
            result = conn.execute(text(f"SHOW DATABASES LIKE '{dbname}';")).fetchone()

            if not result:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS '{dbname}';"))

            result = conn.execute(text(f"SHOW DATABASES LIKE '{dbname}';")).fetchone()

            if result:
                print(f"Database '{dbname}' exists or was created successfully!")  # noqa
            else:
                raise Exception(f"Failed to create the database: '{dbname}'.")
