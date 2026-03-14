"""add_perfil_estudo

Revision ID: e1f2a3b4c5d6
Revises: d1e2f3a4b5c6
Create Date: 2026-03-14 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e1f2a3b4c5d6"
down_revision: Union[str, None] = "d1e2f3a4b5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "perfil_estudo",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("aluno_id", sa.String(length=36), nullable=False),
        sa.Column("area", sa.String(length=100), nullable=False),
        sa.Column(
            "fase_estudo",
            sa.Enum("pre_edital", "pos_edital", name="fase_estudo_enum"),
            nullable=False,
        ),
        sa.Column(
            "experiencia",
            sa.Enum("iniciante", "tempo_de_estudo", name="experiencia_enum"),
            nullable=False,
        ),
        sa.Column("tempo_estudo", sa.String(length=20), nullable=True),
        sa.Column("funcionalidades_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["aluno_id"], ["alunos.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("aluno_id", name="uq_perfil_estudo_aluno_id"),
    )
    with op.batch_alter_table("perfil_estudo", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_perfil_estudo_aluno_id"), ["aluno_id"], unique=True
        )


def downgrade() -> None:
    with op.batch_alter_table("perfil_estudo", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_perfil_estudo_aluno_id"))

    op.drop_table("perfil_estudo")
