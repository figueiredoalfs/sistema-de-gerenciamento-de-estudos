"""add diagnostico to study_tasks

Revision ID: f1a2b3c4d5e6
Revises: e1f2a3b4c5d6
Create Date: 2026-03-14 00:00:00.000000

Mudanças:
- Adiciona "diagnostico" ao enum tipo de study_tasks
- Torna topic_id e subtopic_id nullable (tasks diagnósticas são por matéria, não por subtópico)
- Adiciona coluna questoes_json (TEXT, nullable) para armazenar IDs das questões da bateria
"""
from alembic import op
import sqlalchemy as sa

revision = "f1a2b3c4d5e6"
down_revision = "e1f2a3b4c5d6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("study_tasks", schema=None) as batch_op:
        # Redefine a coluna tipo com o novo enum (batch recria a tabela no SQLite)
        batch_op.alter_column(
            "tipo",
            existing_type=sa.Enum("study", "questions", "review", name="study_task_tipo_enum"),
            type_=sa.Enum("study", "questions", "review", "diagnostico", name="study_task_tipo_enum"),
            existing_nullable=False,
        )
        # Torna topic_id e subtopic_id opcionais (tasks de nível matéria não têm topic/subtopic)
        batch_op.alter_column("topic_id", existing_type=sa.String(36), nullable=True)
        batch_op.alter_column("subtopic_id", existing_type=sa.String(36), nullable=True)

        # Adiciona coluna para lista de questões da bateria diagnóstica
        batch_op.add_column(sa.Column("questoes_json", sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("study_tasks", schema=None) as batch_op:
        batch_op.drop_column("questoes_json")
        batch_op.alter_column("subtopic_id", existing_type=sa.String(36), nullable=False)
        batch_op.alter_column("topic_id", existing_type=sa.String(36), nullable=False)
        batch_op.alter_column(
            "tipo",
            existing_type=sa.Enum("study", "questions", "review", "diagnostico", name="study_task_tipo_enum"),
            type_=sa.Enum("study", "questions", "review", name="study_task_tipo_enum"),
            existing_nullable=False,
        )
