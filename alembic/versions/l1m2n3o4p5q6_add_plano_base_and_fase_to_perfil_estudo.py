"""add plano_base_id and fase_atual to perfil_estudo

Revision ID: l1m2n3o4p5q6
Revises: 6221168b67ff
Create Date: 2026-03-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'l1m2n3o4p5q6'
down_revision = '6221168b67ff'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Cria tabela planos_base (caso ainda não exista via create_all)
    op.create_table(
        'planos_base',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('area', sa.String(100), nullable=False),
        sa.Column('perfil', sa.String(50), nullable=False),
        sa.Column('versao', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('gerado_por_ia', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('revisado_admin', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('fases_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )

    # Adiciona colunas ao perfil_estudo
    with op.batch_alter_table('perfil_estudo') as batch_op:
        batch_op.add_column(
            sa.Column('plano_base_id', sa.String(36), sa.ForeignKey('planos_base.id'), nullable=True)
        )
        batch_op.add_column(
            sa.Column('fase_atual', sa.Integer(), nullable=False, server_default='1')
        )


def downgrade() -> None:
    with op.batch_alter_table('perfil_estudo') as batch_op:
        batch_op.drop_column('fase_atual')
        batch_op.drop_column('plano_base_id')

    op.drop_table('planos_base')
