from database import seed_actions
from database.factories.document_factory import DocumentFactory


class DocumentSeeder:
    name = 'DocumentSeeder'

    @seed_actions
    def __init__(self, rows: int = 30):
        DocumentFactory.create_batch(rows)
