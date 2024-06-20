"""add users user_secrets reservations

Revision ID: caa4483463ca
Revises: 
Create Date: 2024-06-21 01:07:02.920121

"""

import os
from src.common import ignore_passlib_warning

ignore_passlib_warning()

from typing import Sequence, Union
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa
from passlib.context import CryptContext

# revision identifiers, used by Alembic.
revision: str = "caa4483463ca"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


password_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"])


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("role", sa.Enum("basic", "admin", name="roleenum"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_table(
        "reservations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("applicant_count", sa.Integer(), nullable=True),
        sa.Column("is_confirmed", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reservations_id"), "reservations", ["id"], unique=False)
    op.create_index(
        op.f("ix_reservations_user_id"), "reservations", ["user_id"], unique=False
    )
    op.create_table(
        "user_secrets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("hashed_password", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_secrets_id"), "user_secrets", ["id"], unique=False)
    op.create_index(
        op.f("ix_user_secrets_user_id"), "user_secrets", ["user_id"], unique=True
    )
    # ### end Alembic commands ###

    # create admin user
    op.bulk_insert(
        sa.Table(
            "users",
            sa.MetaData(),
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("username", sa.String(), nullable=True),
            sa.Column(
                "role", sa.Enum("basic", "admin", name="roleenum"), nullable=True
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                default=datetime.now(timezone.utc),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                default=datetime.now(timezone.utc),
                onupdate=datetime.now(timezone.utc),
            ),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        ),
        [
            {
                "username": os.environ["ADMIN_USERNAME"],
                "role": "admin",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "deleted_at": None,
            }
        ],
    )

    # Fetch the ID of the newly created admin user
    conn = op.get_bind()
    result = conn.execute(
        sa.text("SELECT id FROM users WHERE username = :username"),
        {"username": os.environ["ADMIN_USERNAME"]},
    )
    admin_user_id = result.fetchone()[0]

    # create user secret for admin user
    op.bulk_insert(
        sa.Table(
            "user_secrets",
            sa.MetaData(),
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("hashed_password", sa.String(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                default=datetime.now(timezone.utc),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                default=datetime.now(timezone.utc),
                onupdate=datetime.now(timezone.utc),
            ),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        ),
        [
            {
                "user_id": admin_user_id,
                "hashed_password": password_context.hash(os.environ["ADMIN_PASSWORD"]),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "deleted_at": None,
            }
        ],
    )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_user_secrets_user_id"), table_name="user_secrets")
    op.drop_index(op.f("ix_user_secrets_id"), table_name="user_secrets")
    op.drop_table("user_secrets")
    op.drop_index(op.f("ix_reservations_user_id"), table_name="reservations")
    op.drop_index(op.f("ix_reservations_id"), table_name="reservations")
    op.drop_table("reservations")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
    # ### end Alembic commands ###