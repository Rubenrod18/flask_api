from app.utils import class_for_name


class Factory():
    models: list = []

    def __init__(self, class_name, num=1):
        factory_name = '_%sFactory' % class_name
        module_name = 'database.factories._%s_factory' % class_name.lower()

        for item in range(num):
            factory_class = class_for_name(module_name, factory_name)
            factory = factory_class()
            self.models.append(factory)

    def make(self, kwargs: dict = None) -> list:
        data = []

        for item in self.models:
            data.append(item.make(**kwargs))

        if len(data) == 1:
            data = data[0]

        return data

    def save(self, **kwargs: dict) -> any:
        data = []

        for model in self.models:
            data.append(model.create(kwargs))

        if len(data) == 1:
            data = data[0]

        return data
