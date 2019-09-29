from app.extensions import db_wrapper
from app.models import get_models


def init_db():
    print('Starting the process of creation of tables...')
    tables = db_wrapper.database.get_tables()

    if len(tables) == 0:
        print('There are not any table created. We\'re going to create them!')
        with db_wrapper.database:
            print('We\'re going to getting database models...')
            models = get_models()
            print('Database models have been gotten succesfully!')

            print('We\'re going to create database tables...')
            db_wrapper.database.create_tables(models)
            print('Database tables have been created!')
    else:
        print('There are %s tables already created!' % len(tables))

    print('Script finished!')