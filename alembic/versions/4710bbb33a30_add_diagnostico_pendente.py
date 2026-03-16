"""add_diagnostico_pendente

Revision ID: 4710bbb33a30
Revises: k1l2m3n4o5p6
Create Date: 2026-03-15 23:17:28.774718

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '4710bbb33a30'
down_revision: Union[str, None] = 'k1l2m3n4o5p6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('alunos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('diagnostico_pendente', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    with op.batch_alter_table('alunos', schema=None) as batch_op:
        batch_op.drop_column('diagnostico_pendente')
