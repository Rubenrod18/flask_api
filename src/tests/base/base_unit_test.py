import pytest


# pylint: disable=attribute-defined-outside-init, unused-argument
class TestBaseUnit:
    @pytest.fixture(autouse=True)
    def setup(self, faker):
        self.faker = faker
