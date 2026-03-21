"""add bancas table and materia column to questoes_banco

Revision ID: n1o2p3q4r5s6
Revises: m1n2o3p4q5r6
Create Date: 2026-03-21 00:00:01.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = 'n1o2p3q4r5s6'
down_revision: Union[str, None] = 'm1n2o3p4q5r6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Cria tabela de bancas
    op.create_table(
        'bancas',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('nome', sa.String(100), nullable=False, unique=True),
        sa.Column('ativo', sa.Boolean(), server_default='1', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

    # Adiciona coluna materia em questoes_banco (nullable para compatibilidade)
    op.add_column(
        'questoes_banco',
        sa.Column('materia', sa.String(200), nullable=True),
    )

    # Backfill: extrai matéria do prefixo do question_code
    connection = op.get_bind()
    rows = connection.execute(
        sa.text("SELECT id, question_code FROM questoes_banco")
    ).fetchall()
    for row in rows:
        qid, qcode = row[0], row[1]
        if qcode:
            # question_code format: DISCIPLINA-BANCA-ANO-SEQ
            prefix = qcode.split('-')[0]  # e.g. "DIREITO_ADMINISTRATIVO"
            materia = prefix.replace('_', ' ').title()
        else:
            materia = ''
        connection.execute(
            sa.text("UPDATE questoes_banco SET materia = :m WHERE id = :id"),
            {"m": materia, "id": qid},
        )


def downgrade() -> None:
    op.drop_column('questoes_banco', 'materia')
    op.drop_table('bancas')
