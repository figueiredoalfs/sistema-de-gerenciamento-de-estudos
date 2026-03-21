"""add materia_pendente to questoes_banco

Revision ID: m1n2o3p4q5r6
Revises: l1m2n3o4p5q6
Create Date: 2026-03-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'm1n2o3p4q5r6'
down_revision: Union[str, None] = 'l1m2n3o4p5q6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'questoes_banco',
        sa.Column('materia_pendente', sa.Boolean(), server_default='0', nullable=False),
    )


def downgrade() -> None:
    op.drop_column('questoes_banco', 'materia_pendente')
