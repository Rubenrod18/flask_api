from app.models.role import Role as RoleModel
from app.models.user import User as UserModel

def init_seed() -> None:
    print(' Seeding roles table...')
    RoleModel.seed()
    print(' Roles table seeded!')

    print(' Seeding users table...')
    UserModel.seed()
    print(' Users table seeded!')
