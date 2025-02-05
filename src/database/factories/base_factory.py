import factory
from faker import Faker
from faker.providers import date_time, person

from app.extensions import db


faker = Faker()
faker.add_provider(person)
faker.add_provider(date_time)


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'flush'

    @classmethod
    def build_dict(cls, exclude: set = None, **kwargs):
        """Builds a dictionary representation of the factory instance.

        Args
        ----
            exclude: set
                List of field names to exclude.
            kwargs:
                Additional fields to override.

        Returns
        -------
            dict:
                The dictionary representation of the factory instance.
        """
        exclude_fields = set(exclude or [])
        instance = cls.build(**kwargs)
        return {
            field: getattr(instance, field)
            for field in cls._meta.declarations.keys()
            if field not in exclude_fields
        }