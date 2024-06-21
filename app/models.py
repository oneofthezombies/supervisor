from datetime import datetime
from typing import Optional
from typing_extensions import Annotated

from sqlalchemy import (
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship, mapped_column, Mapped

from app.common import Role, utcnow
from app import database

IntPk = Annotated[int, mapped_column(primary_key=True)]
CreatedAt = Annotated[datetime, mapped_column(default=utcnow())]
UpdatedAt = Annotated[
    datetime,
    mapped_column(
        default=utcnow(),
        onupdate=utcnow(),
    ),
]
DeletedAt = Annotated[Optional[datetime], mapped_column()]


class User(database.Base):
    __tablename__ = "users"

    id: Mapped[IntPk]
    username: Mapped[str] = mapped_column(unique=True, index=True)
    role: Mapped[Role] = mapped_column(default=Role.basic)
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]
    deleted_at: Mapped[DeletedAt]

    secret = relationship(
        "UserSecret",
        uselist=False,
        back_populates="user",
    )


class UserSecret(database.Base):
    __tablename__ = "user_secrets"

    id: Mapped[IntPk]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        index=True,
    )
    hashed_password: Mapped[str]
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]
    deleted_at: Mapped[DeletedAt]

    user = relationship(
        "User",
        back_populates="secret",
    )


class Reservation(database.Base):
    __tablename__ = "reservations"

    id: Mapped[IntPk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    start_at: Mapped[datetime]
    end_at: Mapped[datetime]
    applicant_count: Mapped[int]
    is_confirmed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]
    deleted_at: Mapped[DeletedAt]

    __table_args__ = (
        Index(
            "ix_reservations_group_confirm",
            "start_at",
            "end_at",
            "is_confirmed",
            "deleted_at",
        ),
    )
