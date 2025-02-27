from app.database.factories.document_factory import DocumentFactory
from app.database.seeds import seed_actions
from app.database.seeds.base_seeder import FactorySeeder


class Seeder(FactorySeeder):
    def __init__(self):
        super().__init__(name='DocumentSeeder', priority=2, factory=DocumentFactory)

    @seed_actions
    def seed(self, rows: int = 30):
        self.factory.create_batch(rows)
