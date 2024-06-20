from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Enum,
)
from sqlalchemy.orm import relationship

from src.common import RoleEnum
from src.modules.db import db_common


class User(db_common.Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.basic)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    deleted_at = Column(DateTime, nullable=True)

    secret = relationship(
        "UserSecret",
        uselist=False,
        back_populates="user",
    )


class UserSecret(db_common.Base):
    __tablename__ = "user_secrets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        index=True,
    )
    hashed_password = Column(String)
    created_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    deleted_at = Column(DateTime, nullable=True)

    user = relationship(
        "User",
        back_populates="secret",
    )


class Reservation(db_common.Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    start_at = Column(DateTime)
    end_at = Column(DateTime)
    applicant_count = Column(Integer)
    is_confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    deleted_at = Column(DateTime, nullable=True)

    __tableargs__ = Index(
        "ix_reservations_confirms",
        "start_at",
        "end_at",
        "is_confirmed",
        "deleted_at",
    )
