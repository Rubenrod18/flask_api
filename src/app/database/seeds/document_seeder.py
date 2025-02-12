from app.database import seed_actions
from app.database.factories.document_factory import DocumentFactory


class Seeder:
    name = 'DocumentSeeder'
    priority = 2

    @seed_actions
    def __init__(self, rows: int = 30):
        DocumentFactory.create_batch(rows)
