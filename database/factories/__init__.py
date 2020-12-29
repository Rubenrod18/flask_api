"""Package contains factories modules.

A factory is a database model filled with fake data. The factory purposes is
creating records in a simple way.

The module is used in testing and seeds.

References
----------
The factory concept is based on `Laravel factories
<https://laravel.com/docs/8.x/database-testing#using-factories>`_

"""
import os

from app.utils import get_attr_from_module


class Factory:
    """Class for managing factories based on database models.

    Create and save instances of database models or dicts based on
    database models registered in the application.

    Methods
    -------
    make(self, params: dict = None, to_dict: bool = False, exclude: list = None)
        Create instances of database models with fake data.
    save(self, params: dict = None)
        Save instances of database models in the database.

    Examples
    --------
    How to create a fake user without save in database from command line::

        source venv/bin/activate
        flask shell
        >>> user_factory = Factory('User')
        >>> user = user_factory.make()  # An instance of database model
        <User: None>
        >>> user.__data__  # You can see user data on this way

    Oh, Wait!

    >>> from pprint import pprint
    >>> pprint(user.__data__)  # Even better!

    You can save the user in the database.

    >>> user.save()
    1

    Factory can create a dictionary instead of an instance of database model.

    >>> user = user_factory.make(to_dict=True)
    >>> pprint(user)

    Also can set params too.

    >>> user_factory = Factory('User')
    >>> user = user_factory.make({'name': 'Ruben', 'last_name': 'Rodriguez'})
    >>> user.name
    'Ruben'
    >>> user.last_name
    'Rodriguez'

    Factory allow to make many users in once time.

    >>> user_factory = Factory('User', 3)
    >>> users = user_factory.make()
    [<User: None>, <User: None>, <User: None>]

    If you want to fill some params later then you can pass a fieldnames list
    to the factory of thats fields that you don't want to fill yet.

    >>> user_factory = Factory('User')
    >>> user = user_factory.make(exclude=['name', 'birth_date'])
    >>> user.name
    None
    >>> user.birth_date
    None

    If you only need to save data you can do it.

    >>> Factory('User', 3).save()
    [<User: 1>, <User: 2>, <User: 3>]

    And you can set params for all users.

    >>> Factory('User', 3).save({'name': 'Ruben'})
    [<User: 4>, <User: 5>, <User: 6>]

    """
    __models: list = None
    # FIXME: it's not the best way
    __current_module = 'database.factories'

    def __init__(self, model_name: str, records: int = 1):
        """Register as many factories as given records."""
        self.__models = []

        factory_classname = '_%sFactory' % model_name
        factory_basename = '_%s_factory' % model_name.lower()
        factory_module = f'{self.__current_module}.{factory_basename}'

        self.__check_exists_factory(factory_classname, model_name)

        for item in range(records):
            factory_class = get_attr_from_module(factory_module, factory_classname)
            factory = factory_class()
            self.__models.append(factory)

    def make(self, params: dict = None, to_dict: bool = False,
             exclude: list = None) -> any:
        """Create instances of database model with fake data.

        Parameters
        ----------
        params : dict
            Params to set when an instance of database model is created.
        to_dict : bool
            If is True returns a dict otherwise is an instance of database model.
            By default is False.
        exclude: list
            Params are not going to be filled. These fields are equals to None.

        Returns
        -------
        any
            Could be a dict, a list or an instance of database model.

        """
        params = params or {}
        exclude = exclude or []

        data = []

        for item in self.__models:
            data.append(item.make(params, to_dict, exclude))

        if len(data) == 1:
            data = data[0]

        return data

    def save(self, params: dict = None) -> any:
        """Save instances of database model in the database.

        Parameters
        ----------
        params : dict
            Params to set when an instance of database model is created.

        Returns
        -------
        any
            Could be a list or an instance of database model.

        """
        params = params or {}

        if len(self.__models) == 1:
            data = self.__models[0].create(params)
        else:
            model = self.__models[0]
            data = model.bulk_create(len(self.__models), params)

        return data

    def __check_exists_factory(self, factory_classname: str,
                               model_name: str) -> None:
        abs_path = os.path.realpath(__file__)
        dirname = os.path.dirname(abs_path)
        current_dir_files = os.listdir(dirname)

        files = set(
            file for file in current_dir_files
            if file.endswith('.py') and file != os.path.basename(__file__)
        )
        factories_classnames = set()

        for filename in files:
            basename = filename[:-3]
            classname = '_%s' % basename.title().replace('_', '')

            module = f'{self.__current_module}.{basename}'

            factory_class = get_attr_from_module(module, classname)
            factories_classnames.add(factory_class().__class__.__name__)

        if factory_classname not in factories_classnames:
            raise NameError(f'model \'{model_name}\' is not registered')
