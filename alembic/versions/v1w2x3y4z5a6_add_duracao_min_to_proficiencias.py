"""add duracao_min to proficiencias

Revision ID: v1w2x3y4z5a6
Revises: u1v2w3x4y5z6
Create Date: 2026-03-28 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'v1w2x3y4z5a6'
down_revision = 'u1v2w3x4y5z6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('proficiencias', sa.Column('duracao_min', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('proficiencias', 'duracao_min')
