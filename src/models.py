from sqlalchemy import Column, Integer, String, Enum

from src.common import RoleEnum
from src.modules.db import db_common


class User(db_common.Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(RoleEnum), default=RoleEnum.basic)
