import factory

from app.extensions import db


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

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
        return {field: getattr(instance, field) for field in cls._meta.declarations if field not in exclude_fields}
