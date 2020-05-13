from database.factories import Factory
from database.seeds import seed_actions


class DocumentSeeder():
    name = 'DocumentSeeder'

    @seed_actions
    def __init__(self, rows: int = 30):
        Factory('Document', rows).save()
