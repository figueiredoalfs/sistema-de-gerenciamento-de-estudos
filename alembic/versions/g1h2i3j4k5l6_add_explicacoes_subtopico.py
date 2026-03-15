"""add explicacoes_subtopico table

Revision ID: g1h2i3j4k5l6
Revises: f1a2b3c4d5e6
Create Date: 2026-03-15 00:00:00.000000

Mudanças:
- Cria tabela explicacoes_subtopico para cache de explicações geradas pela IA
- UNIQUE constraint em topico_id garante uma explicação por subtópico
"""
import sqlalchemy as sa
from alembic import op

revision = "g1h2i3j4k5l6"
down_revision = "f1a2b3c4d5e6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "explicacoes_subtopico",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("topico_id", sa.String(36), sa.ForeignKey("topicos.id"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("topico_id", name="uq_explicacao_topico"),
    )
    op.create_index("ix_explicacoes_subtopico_topico_id", "explicacoes_subtopico", ["topico_id"])


def downgrade() -> None:
    op.drop_index("ix_explicacoes_subtopico_topico_id", table_name="explicacoes_subtopico")
    op.drop_table("explicacoes_subtopico")
