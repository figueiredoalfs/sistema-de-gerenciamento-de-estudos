"""add_questoes_table

Revision ID: b1c2d3e4f5a6
Revises: a1b2c3d4e5f6
Create Date: 2026-03-14 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "questoes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("subject_id", sa.String(36), sa.ForeignKey("topicos.id"), nullable=False),
        sa.Column("topic_id", sa.String(36), sa.ForeignKey("topicos.id"), nullable=False),
        sa.Column("subtopic_id", sa.String(36), sa.ForeignKey("topicos.id"), nullable=False),
        sa.Column("enunciado", sa.Text, nullable=False),
        sa.Column("alternativas_json", sa.Text, nullable=False),
        sa.Column("resposta_correta", sa.String(1), nullable=False),
        sa.Column(
            "fonte",
            sa.Enum(
                "ia", "admin", "qconcursos", "tec", "prova_real", "simulado",
                name="fonte_questao_enum",
            ),
            nullable=False,
            server_default="admin",
        ),
        sa.Column("banca", sa.String(100), nullable=True),
        sa.Column("ano", sa.Integer, nullable=True),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("questoes")
