import os

from app.utils import class_for_name


class Factory:
    __models: list = None
    # FIXME: it's not the best way
    __current_module = 'database.factories'

    def __init__(self, model_name: str, records: int = 1):
        self.__models = []

        factory_classname = '_%sFactory' % model_name
        factory_basename = '_%s_factory' % model_name.lower()
        factory_module = f'{self.__current_module}.{factory_basename}'

        self.__check_exists_factory(factory_classname, model_name)

        for item in range(records):
            factory_class = class_for_name(factory_module, factory_classname)
            factory = factory_class()
            self.__models.append(factory)

    def make(self, params: dict = None, to_dict: bool = False,
             exclude: list = None) -> any:
        params = params or {}
        exclude = exclude or []

        data = []

        for item in self.__models:
            data.append(item.make(params, to_dict, exclude))

        if len(data) == 1:
            data = data[0]

        return data

    def save(self, params: dict = None) -> any:
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

            factory_class = class_for_name(module, classname)
            factories_classnames.add(factory_class().__class__.__name__)

        if factory_classname not in factories_classnames:
            raise NameError(f'model \'{model_name}\' is not registered')
