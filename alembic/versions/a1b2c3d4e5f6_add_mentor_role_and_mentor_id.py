"""add_mentor_role_and_mentor_id

Revision ID: a1b2c3d4e5f6
Revises: 3c1a7670028f
Create Date: 2026-03-14 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '3c1a7670028f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Migrar registros 'aluno' para 'student' antes de alterar a tabela
    op.execute("UPDATE alunos SET role = 'student' WHERE role = 'aluno'")

    # SQLite não suporta ALTER COLUMN diretamente — usamos batch_alter_table
    with op.batch_alter_table("alunos", schema=None) as batch_op:
        batch_op.alter_column(
            "role",
            existing_type=sa.Enum("admin", "aluno", name="role_enum"),
            type_=sa.Enum("admin", "mentor", "student", name="role_enum"),
            existing_nullable=False,
        )
        batch_op.add_column(
            sa.Column("mentor_id", sa.String(length=36), nullable=True)
        )
        batch_op.create_foreign_key(
            "fk_alunos_mentor_id", "alunos", ["mentor_id"], ["id"]
        )


def downgrade() -> None:
    with op.batch_alter_table("alunos", schema=None) as batch_op:
        batch_op.drop_constraint("fk_alunos_mentor_id", type_="foreignkey")
        batch_op.drop_column("mentor_id")
        batch_op.alter_column(
            "role",
            existing_type=sa.Enum("admin", "mentor", "student", name="role_enum"),
            type_=sa.Enum("admin", "aluno", name="role_enum"),
            existing_nullable=False,
        )

    op.execute("UPDATE alunos SET role = 'aluno' WHERE role = 'student'")
