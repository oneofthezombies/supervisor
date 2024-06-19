import enum
import os


def database_url(async_=True):
    protocol = ""
    if async_:
        protocol = "postgresql+asyncpg"
    else:
        protocol = "postgresql+psycopg2"

    return f"{protocol}://{os.environ['DB_USERNAME']}:{os.environ['DB_PASSWORD']}@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/supervisor"


class RoleEnum(str, enum.Enum):
    basic = "basic"
    admin = "admin"
