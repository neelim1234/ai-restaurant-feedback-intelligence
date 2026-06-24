"""add_feedback_date_index

Revision ID: 9a4627cd3a5a
Revises: f76789c751be
Create Date: 2026-06-19 01:39:53.880331

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a4627cd3a5a'
down_revision: Union[str, None] = 'f76789c751be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('ix_feedbacks_feedback_date', 'feedbacks', ['feedback_date'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_feedbacks_feedback_date', table_name='feedbacks')

