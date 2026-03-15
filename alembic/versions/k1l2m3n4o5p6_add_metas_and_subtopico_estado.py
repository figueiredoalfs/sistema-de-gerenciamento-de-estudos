"""add metas and subtopico_estados tables; add goal_id to study_tasks

Revision ID: k1l2m3n4o5p6
Revises: j1k2l3m4n5o6
Create Date: 2026-03-15 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "k1l2m3n4o5p6"
down_revision = "j1k2l3m4n5o6"
branch_labels = None
depends_on = None


def upgrade():
    # 1. Tabela metas
    op.create_table(
        "metas",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("aluno_id", sa.String(36), sa.ForeignKey("alunos.id"), nullable=False),
        sa.Column("numero_semana", sa.Integer(), nullable=False),
        sa.Column("tasks_meta", sa.Integer(), nullable=False),
        sa.Column("tasks_concluidas", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="aberta"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_metas_aluno_id", "metas", ["aluno_id"])

    # 2. Tabela subtopico_estados (UniqueConstraint declarada no create_table — exigido pelo SQLite)
    op.create_table(
        "subtopico_estados",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("aluno_id", sa.String(36), sa.ForeignKey("alunos.id"), nullable=False),
        sa.Column("subtopico_id", sa.String(36), sa.ForeignKey("topicos.id"), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default="novo"),
        sa.Column("exposure_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("accuracy_rate", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("ultima_exposicao", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("aluno_id", "subtopico_id", name="uq_subtopico_estado_aluno"),
    )
    op.create_index("ix_subtopico_estados_aluno_id", "subtopico_estados", ["aluno_id"])
    op.create_index("ix_subtopico_estados_subtopico_id", "subtopico_estados", ["subtopico_id"])

    # 3. Adiciona goal_id em study_tasks (batch_alter_table obrigatório no SQLite para FKs)
    with op.batch_alter_table("study_tasks", recreate="auto") as batch_op:
        batch_op.add_column(
            sa.Column("goal_id", sa.String(36), sa.ForeignKey("metas.id"), nullable=True)
        )
        batch_op.create_index("ix_study_tasks_goal_id", ["goal_id"])


def downgrade():
    with op.batch_alter_table("study_tasks", recreate="auto") as batch_op:
        batch_op.drop_index("ix_study_tasks_goal_id")
        batch_op.drop_column("goal_id")

    op.drop_table("subtopico_estados")
    op.drop_table("metas")
