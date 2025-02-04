from database import seed_actions
from database.factories import Factory


class DocumentSeeder:
    name = 'DocumentSeeder'

    @seed_actions
    def __init__(self, rows: int = 30):
        Factory('Document', rows).save()
