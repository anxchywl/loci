"""reorder categories: urban_legends second after love

Revision ID: c4d5e6f7a8b9
Revises: b3b805814152
Create Date: 2026-07-12

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c4d5e6f7a8b9"
down_revision: Union[str, None] = "b3b805814152"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# slug -> position. Love stays first, urban_legends moves to second,
# everything else shifts down by one.
NEW_POSITIONS = {
    "love": 1,
    "urban_legends": 2,
    "happy_moments": 3,
    "dreams": 4,
    "education": 5,
    "career": 6,
    "travel": 7,
    "friendship": 8,
    "childhood": 9,
    "achievements": 10,
    "beautiful_places": 11,
    "memories": 12,
}

# Original ordering from the initial schema.
OLD_POSITIONS = {
    "love": 1,
    "happy_moments": 2,
    "dreams": 3,
    "education": 4,
    "career": 5,
    "travel": 6,
    "friendship": 7,
    "childhood": 8,
    "achievements": 9,
    "beautiful_places": 10,
    "memories": 11,
    "urban_legends": 12,
}


def _apply(positions: dict[str, int]) -> None:
    for slug, position in positions.items():
        op.execute(
            f"UPDATE categories SET position = {position} WHERE slug = '{slug}'"
        )


def upgrade() -> None:
    _apply(NEW_POSITIONS)


def downgrade() -> None:
    _apply(OLD_POSITIONS)
