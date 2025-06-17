import pytest

from tests.base.base_api_test import TestBaseApi


# pylint: disable=attribute-defined-outside-init, unused-argument
class _TestBaseUserEndpointsTest(TestBaseApi):
    @pytest.fixture(autouse=True)
    def base_setup(self, setup):
        self.base_path = f'{self.base_path}/users'
