"""add ciclo_materias table

Revision ID: s1t2u3v4w5x6
Revises: r1s2t3u4v5w6
Create Date: 2026-03-22 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 's1t2u3v4w5x6'
down_revision = 'r1s2t3u4v5w6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'ciclo_materias',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('area', sa.String(100), nullable=False),
        sa.Column('subject_id', sa.String(36), sa.ForeignKey('topicos.id'), nullable=False),
        sa.Column('ordem', sa.Integer, nullable=False, server_default='0'),
        sa.Column('ativo', sa.Boolean, server_default='1'),
        sa.Column('created_at', sa.DateTime, nullable=True),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )
    op.create_index('ix_ciclo_materias_area', 'ciclo_materias', ['area'])


def downgrade() -> None:
    op.drop_index('ix_ciclo_materias_area', table_name='ciclo_materias')
    op.drop_table('ciclo_materias')
