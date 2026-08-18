"""merge heads

Revision ID: 91ed44395060
Revises: 51e70c0ebba2, 6f2037137e48
Create Date: 2026-08-17 15:38:18.325588

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '91ed44395060'
down_revision: Union[str, Sequence[str], None] = ('51e70c0ebba2', '6f2037137e48')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
