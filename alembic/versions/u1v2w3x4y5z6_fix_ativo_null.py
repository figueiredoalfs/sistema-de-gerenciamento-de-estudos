"""fix ativo null — set default true and backfill

Revision ID: u1v2w3x4y5z6
Revises: t1u2v3w4x5y6
Create Date: 2026-03-24 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'u1v2w3x4y5z6'
down_revision = 't1u2v3w4x5y6'
branch_labels = None
depends_on = None


def upgrade():
    # Backfill NULL → True para todos os usuários existentes
    op.execute("UPDATE alunos SET ativo = TRUE WHERE ativo IS NULL")
    # Garante que novas inserções sem valor explícito usem TRUE
    op.alter_column('alunos', 'ativo',
                    existing_type=sa.Boolean(),
                    nullable=False,
                    server_default=sa.true())


def downgrade():
    op.alter_column('alunos', 'ativo',
                    existing_type=sa.Boolean(),
                    nullable=True,
                    server_default=None)
