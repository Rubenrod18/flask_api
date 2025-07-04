from tests.factories.document_factory import DocumentFactory
from tests.seeds import seed_actions
from tests.seeds.base_seeder import FactorySeeder


class Seeder(FactorySeeder):
    def __init__(self):
        super().__init__(name='DocumentSeeder', priority=2, factory=DocumentFactory)
        self._default_rows = 30

    @seed_actions
    def seed(self, rows: int = None) -> None:
        self.factory.create_batch(rows or self._default_rows)
