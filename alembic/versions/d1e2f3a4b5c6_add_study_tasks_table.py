"""add study_tasks table and drop study_sessions

Revision ID: d1e2f3a4b5c6
Revises: c1d2e3f4a5b6
Create Date: 2026-03-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "d1e2f3a4b5c6"
down_revision = "c1d2e3f4a5b6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    # Cria a nova tabela de tasks de estudo
    op.create_table(
        "study_tasks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("aluno_id", sa.String(36), sa.ForeignKey("alunos.id"), nullable=False),
        sa.Column("subject_id", sa.String(36), sa.ForeignKey("topicos.id"), nullable=False),
        sa.Column("topic_id", sa.String(36), sa.ForeignKey("topicos.id"), nullable=False),
        sa.Column("subtopic_id", sa.String(36), sa.ForeignKey("topicos.id"), nullable=False),
        sa.Column(
            "tipo",
            sa.Enum("study", "questions", "review", name="study_task_tipo_enum"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("pending", "in_progress", "completed", name="study_task_status_enum"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )
    op.create_index("ix_study_tasks_aluno_id", "study_tasks", ["aluno_id"])
    op.create_index("ix_study_tasks_subtopic_id", "study_tasks", ["subtopic_id"])

    # Remove a tabela legada study_sessions (sem dados, FK para topics legados)
    # No PostgreSQL em produção (banco novo), study_sessions pode não existir
    if dialect == 'postgresql':
        result = bind.execute(sa.text("SELECT to_regclass('public.study_sessions')"))
        if result.scalar() is not None:
            op.execute("ALTER TABLE study_sessions DROP CONSTRAINT IF EXISTS fk_study_sessions_topic_id")
            op.drop_table("study_sessions")
    else:
        with op.batch_alter_table("study_sessions") as batch_op:
            batch_op.drop_constraint("fk_study_sessions_topic_id", type_="foreignkey")
        op.drop_table("study_sessions")


def downgrade() -> None:
    op.drop_index("ix_study_tasks_subtopic_id", table_name="study_tasks")
    op.drop_index("ix_study_tasks_aluno_id", table_name="study_tasks")
    op.drop_table("study_tasks")

    # Recria study_sessions para reversão
    op.create_table(
        "study_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("alunos.id"), nullable=False),
        sa.Column("topic_id", sa.String(36), sa.ForeignKey("topics.id"), nullable=False),
        sa.Column(
            "tipo",
            sa.Enum("study_theory", "review", "practice", name="study_session_tipo_enum"),
            nullable=False,
        ),
        sa.Column("data_agendada", sa.DateTime, nullable=True),
        sa.Column(
            "status",
            sa.Enum("pending", "done", "skipped", name="study_session_status_enum"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )
