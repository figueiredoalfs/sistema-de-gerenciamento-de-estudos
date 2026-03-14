"""add respostas_questoes table

Revision ID: c1d2e3f4a5b6
Revises: b1c2d3e4f5a6
Create Date: 2026-03-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "c1d2e3f4a5b6"
down_revision = "b1c2d3e4f5a6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "respostas_questoes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("aluno_id", sa.String(36), sa.ForeignKey("alunos.id"), nullable=False),
        sa.Column("questao_id", sa.String(36), sa.ForeignKey("questoes.id"), nullable=False),
        sa.Column("subtopico_id", sa.String(36), sa.ForeignKey("topicos.id"), nullable=False),
        sa.Column("resposta_dada", sa.String(1), nullable=False),
        sa.Column("correta", sa.Boolean, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )
    op.create_index("ix_respostas_questoes_aluno_id", "respostas_questoes", ["aluno_id"])
    op.create_index("ix_respostas_questoes_questao_id", "respostas_questoes", ["questao_id"])
    op.create_index("ix_respostas_questoes_subtopico_id", "respostas_questoes", ["subtopico_id"])


def downgrade() -> None:
    op.drop_index("ix_respostas_questoes_subtopico_id", table_name="respostas_questoes")
    op.drop_index("ix_respostas_questoes_questao_id", table_name="respostas_questoes")
    op.drop_index("ix_respostas_questoes_aluno_id", table_name="respostas_questoes")
    op.drop_table("respostas_questoes")
