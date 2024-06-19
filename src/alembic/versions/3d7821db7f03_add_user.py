"""add user

Revision ID: 3d7821db7f03
Revises: 
Create Date: 2024-06-20 02:03:53.843481

"""

from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa

# ignore passlib warning begin
import bcrypt


class About:
    pass


if not hasattr(bcrypt, "__about__"):
    about = About()
    setattr(about, "__version__", "1.0.0")
    setattr(bcrypt, "__about__", about)
# ignore passlib warning end

from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# revision identifiers, used by Alembic.
revision: str = "3d7821db7f03"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("hashed_password", sa.String(), nullable=True),
        sa.Column("role", sa.Enum("basic", "admin", name="roleenum"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    # ### end Alembic commands ###

    # create admin user
    op.bulk_insert(
        sa.Table(
            "users",
            sa.MetaData(),
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("username", sa.String(), nullable=True),
            sa.Column("hashed_password", sa.String(), nullable=True),
            sa.Column(
                "role", sa.Enum("basic", "admin", name="roleenum"), nullable=True
            ),
        ),
        [
            {
                "username": os.environ["ADMIN_USERNAME"],
                "hashed_password": password_context.hash(os.environ["ADMIN_PASSWORD"]),
                "role": "admin",
            }
        ],
    )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
    # ### end Alembic commands ###
