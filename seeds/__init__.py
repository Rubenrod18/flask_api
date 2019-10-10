from app.models.user import User


def init_seed() -> None:
    """This is used for inserting fake data in database tables."""
    print(' Seeding users table...')

    for i in range(10):
        User.seed()

    print(' Users table seeded!')
    return None
