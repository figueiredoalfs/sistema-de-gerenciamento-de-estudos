"""add codigos_convite table

Revision ID: t1u2v3w4x5y6
Revises: s1t2u3v4w5x6
Create Date: 2026-03-24 00:00:00.000000

"""
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa

revision = 't1u2v3w4x5y6'
down_revision = 's1t2u3v4w5x6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'codigos_convite',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('codigo', sa.String(50), unique=True, nullable=False),
        sa.Column('descricao', sa.String(200), nullable=True),
        sa.Column('usos_maximos', sa.Integer(), nullable=True),
        sa.Column('usos_atuais', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_codigos_convite_codigo', 'codigos_convite', ['codigo'], unique=True)

    # Seed: código padrão para o beta
    op.execute(
        sa.text(
            "INSERT INTO codigos_convite (id, codigo, descricao, usos_maximos, usos_atuais, ativo, created_at) "
            "VALUES (:id, :codigo, :descricao, NULL, 0, TRUE, :created_at)"
        ).bindparams(
            id='00000000-0000-0000-0000-000000000001',
            codigo='BETA2026',
            descricao='Código padrão beta — acesso irrestrito',
            created_at=datetime.now(timezone.utc),
        )
    )


def downgrade():
    op.drop_index('ix_codigos_convite_codigo', table_name='codigos_convite')
    op.drop_table('codigos_convite')
