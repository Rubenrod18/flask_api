from faker import Faker
from faker.providers import person
from faker.providers import date_time

from app.models.user import User


def init_seed() -> None:
    """This is used for inserting fake data in database tables."""
    print(' Seeding users table...')
    fake = Faker()
    fake.add_provider(person)
    fake.add_provider(date_time)

    for i in range(100):
        User.seed(fake)

    print(' Users table seeded!')
    return None
