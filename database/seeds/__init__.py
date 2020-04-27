from app.models.role import Role as RoleModel
from app.models.user import User as UserModel


def init_seed() -> None:
    print(' Seeding roles table...')

    for i in range(10):
        RoleModel.seed()

    print(' Roles table seeded!')

    print(' Seeding users table...')

    for i in range(100):
        UserModel.seed()

    print(' Users table seeded!')
