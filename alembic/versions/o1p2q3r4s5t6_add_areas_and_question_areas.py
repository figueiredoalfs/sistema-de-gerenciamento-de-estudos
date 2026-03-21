"""add areas table and question_areas junction table

Revision ID: o1p2q3r4s5t6
Revises: n1o2p3q4r5s6
Create Date: 2026-03-21 12:00:00.000000

"""
from typing import Sequence, Union
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "o1p2q3r4s5t6"
down_revision: Union[str, None] = "n1o2p3q4r5s6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_AREAS_PADRAO = [
    "Fiscal",
    "Controle",
    "Policial",
    "Jurídica",
    "TI",
    "Saúde",
    "Pedagógica",
    "Gestão",
    "Ambiental",
]


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = inspector.get_table_names()

    if "areas" not in existing_tables:
        op.create_table(
            "areas",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("nome", sa.String(100), nullable=False, unique=True),
            sa.Column("ativo", sa.Boolean(), server_default="1", nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
        )
        # Seed das áreas padrão (só insere se criou agora)
        for nome in _AREAS_PADRAO:
            bind.execute(
                sa.text("INSERT INTO areas (id, nome) VALUES (:id, :nome)"),
                {"id": str(uuid.uuid4()), "nome": nome},
            )

    if "question_areas" not in existing_tables:
        op.create_table(
            "question_areas",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "question_id",
                sa.String(36),
                sa.ForeignKey("questoes_banco.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "area_id",
                sa.String(36),
                sa.ForeignKey("areas.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("fonte", sa.String(10), nullable=False, server_default="manual"),
            sa.UniqueConstraint("question_id", "area_id", name="uq_question_area"),
        )
        op.create_index("ix_qa_question_id", "question_areas", ["question_id"])
        op.create_index("ix_qa_area_id", "question_areas", ["area_id"])


def downgrade() -> None:
    op.drop_index("ix_qa_area_id", table_name="question_areas")
    op.drop_index("ix_qa_question_id", table_name="question_areas")
    op.drop_table("question_areas")
    op.drop_table("areas")
