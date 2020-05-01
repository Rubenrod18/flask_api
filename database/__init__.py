from faker import Faker
from faker.providers import person
from faker.providers import date_time

fake = Faker()
fake.add_provider(person)
fake.add_provider(date_time)