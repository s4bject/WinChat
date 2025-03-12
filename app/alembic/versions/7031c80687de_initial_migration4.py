"""Initial migration4

Revision ID: 7031c80687de
Revises: 504cb6f95b85
Create Date: 2025-03-10 18:30:38.251148

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7031c80687de'
down_revision: Union[str, None] = '504cb6f95b85'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('chats', 'name')
    op.drop_column('chats', 'type')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chats', sa.Column('type', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('chats', sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
