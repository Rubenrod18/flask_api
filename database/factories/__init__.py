from app.utils import class_for_name


class Factory():
    models: list = None

    def __init__(self, class_name, num: int = 1):
        factory_name = '_%sFactory' % class_name
        module_name = 'database.factories._%s_factory' % class_name.lower()

        self.models = []

        for item in range(num):
            factory_class = class_for_name(module_name, factory_name)
            factory = factory_class()
            self.models.append(factory)

    def make(self, params: dict = None, to_dict: bool = False, exclude: list = None) -> any:
        params = params or {}
        exclude = exclude or []

        data = []

        for item in self.models:
            data.append(item.make(params, to_dict, exclude))

        if len(data) == 1:
            data = data[0]

        return data

    def save(self, params: dict = None) -> any:
        params = params or {}

        if len(self.models) == 1:
            data = self.models[0].create(params)
        else:
            model = self.models[0]
            model.bulk_create(len(self.models), params)
            data = True

        return data
