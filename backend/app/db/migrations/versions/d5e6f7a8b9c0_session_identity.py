"""bind access tokens to revocable refresh sessions"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "d5e6f7a8b9c0"
down_revision: Union[str, None] = "c4d5e6f7a8b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "refresh_tokens",
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=True,
        ),
    )
    op.execute(
        "UPDATE refresh_tokens SET session_id = gen_random_uuid() WHERE session_id IS NULL"
    )
    op.alter_column("refresh_tokens", "session_id", nullable=False)
    op.create_index(
        "ix_refresh_tokens_session_active",
        "refresh_tokens",
        ["session_id", "revoked_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_refresh_tokens_session_active", table_name="refresh_tokens")
    op.drop_column("refresh_tokens", "session_id")
