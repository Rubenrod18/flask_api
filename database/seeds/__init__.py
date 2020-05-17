from app.extensions import db_wrapper
from database.seeds.role_seeder import RoleSeeder
from database.seeds.user_seeder import UserSeeder
from database.seeds.document_seeder import DocumentSeeder


def get_seeders() -> list:
    return [
        RoleSeeder,
        UserSeeder,
        DocumentSeeder,
    ]


def init_seed() -> None:
    seeders = get_seeders()

    with db_wrapper.database.atomic():
        for seed in seeders:
            seed()
        print(' Database seeding completed successfully.')
    db_wrapper.database.close()
