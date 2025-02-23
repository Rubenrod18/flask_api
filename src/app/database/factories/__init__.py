from faker import Faker
from faker.providers import date_time, file, person

faker = Faker()
faker.add_provider(person)
faker.add_provider(date_time)
faker.add_provider(file)
