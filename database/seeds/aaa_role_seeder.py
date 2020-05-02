from database.factories import Factory
from database.seeds import seed_actions

class RoleSeeder():
    name = 'RoleSeeder'

    @seed_actions
    def __init__(self, rows: int = 10):
        Factory('Role', rows).save()