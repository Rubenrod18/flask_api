from app.models.user import User as UserModel


def init_seed() -> None:
    print(' Seeding users table...')

    for i in range(100):
        UserModel.seed()

    print(' Users table seeded!')
