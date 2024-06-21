from datetime import datetime, timezone
import enum
import os


def ignore_passlib_warning():
    import bcrypt

    class About:
        pass

    if not hasattr(bcrypt, "__about__"):
        about = About()
        setattr(about, "__version__", "1.0.0")
        setattr(bcrypt, "__about__", about)


def database_url(async_=True):
    protocol = ""
    if async_:
        protocol = "postgresql+asyncpg"
    else:
        protocol = "postgresql+psycopg2"

    return f"{protocol}://{os.environ['DB_USERNAME']}:{os.environ['DB_PASSWORD']}@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/supervisor"


def utcnow():
    return datetime.now(timezone.utc)


class Role(enum.Enum):
    basic = "basic"
    admin = "admin"
