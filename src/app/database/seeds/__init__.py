from app.extensions import db
from app.database.seeds.role_seeder import RoleSeeder
from app.database.seeds.user_seeder import UserSeeder
from app.database.seeds.document_seeder import DocumentSeeder


def get_seeders() -> list:
    return [
        RoleSeeder,
        UserSeeder,
        DocumentSeeder,
    ]


def init_seed() -> None:
    seeders = get_seeders()

    for seed in seeders:
        seed()

    db.session.commit()
    print(' Database seeding completed successfully.')
