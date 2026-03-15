"""add questoes_banco and question_subtopics tables

Revision ID: h1i2j3k4l5m6
Revises: g1h2i3j4k5l6
Create Date: 2026-03-15 00:00:00.000000

Mudanças:
- Cria tabela questoes_banco para banco de questões importadas
- Cria tabela question_subtopics com coluna fonte (ia | manual)
- Lida com tabelas já existentes criadas via create_all (dev)
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "h1i2j3k4l5m6"
down_revision = "g1h2i3j4k5l6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = inspector.get_table_names()

    if "questoes_banco" not in existing_tables:
        op.create_table(
            "questoes_banco",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("question_code", sa.String(50), nullable=False, unique=True),
            sa.Column("subject", sa.String(200), nullable=False),
            sa.Column("statement", sa.Text(), nullable=False),
            sa.Column("alternatives_json", sa.Text(), nullable=False),
            sa.Column("correct_answer", sa.String(1), nullable=False),
            sa.Column("board", sa.String(100), nullable=True),
            sa.Column("year", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_questoes_banco_question_code", "questoes_banco", ["question_code"])

    if "question_subtopics" not in existing_tables:
        op.create_table(
            "question_subtopics",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "question_id",
                sa.String(36),
                sa.ForeignKey("questoes_banco.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "subtopic_id",
                sa.String(36),
                sa.ForeignKey("topicos.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("fonte", sa.String(10), nullable=False, server_default="manual"),
            sa.UniqueConstraint("question_id", "subtopic_id", name="uq_question_subtopic"),
        )
        op.create_index("ix_qs_question_id", "question_subtopics", ["question_id"])
        op.create_index("ix_qs_subtopic_id", "question_subtopics", ["subtopic_id"])
    else:
        # Tabela já existe (criada via create_all): adicionar coluna fonte se ausente
        existing_cols = {col["name"] for col in inspector.get_columns("question_subtopics")}
        if "fonte" not in existing_cols:
            op.add_column(
                "question_subtopics",
                sa.Column("fonte", sa.String(10), nullable=False, server_default="manual"),
            )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = inspector.get_table_names()

    if "question_subtopics" in existing_tables:
        op.drop_index("ix_qs_subtopic_id", table_name="question_subtopics")
        op.drop_index("ix_qs_question_id", table_name="question_subtopics")
        op.drop_table("question_subtopics")

    if "questoes_banco" in existing_tables:
        op.drop_index("ix_questoes_banco_question_code", table_name="questoes_banco")
        op.drop_table("questoes_banco")
