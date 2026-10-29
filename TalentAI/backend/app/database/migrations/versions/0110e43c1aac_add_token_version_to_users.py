
"""add token version to users

Revision ID: 0110e43c1aac
Revises: 9ef83d08da5a
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0110e43c1aac"
down_revision: Union[str, Sequence[str], None] = "9ef83d08da5a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "token_version",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "token_version")
