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
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == 'postgresql':
        # PostgreSQL: recriar o enum com os novos valores e migrar a coluna
        op.execute("""
            CREATE TYPE role_enum_new AS ENUM ('admin', 'mentor', 'student')
        """)
        op.execute("""
            ALTER TABLE alunos
            ALTER COLUMN role TYPE role_enum_new
            USING (CASE role::text
                   WHEN 'aluno' THEN 'student'::role_enum_new
                   ELSE role::text::role_enum_new
                   END)
        """)
        op.execute("DROP TYPE role_enum")
        op.execute("ALTER TYPE role_enum_new RENAME TO role_enum")
        op.add_column('alunos', sa.Column('mentor_id', sa.String(length=36), nullable=True))
        op.create_foreign_key('fk_alunos_mentor_id', 'alunos', 'alunos', ['mentor_id'], ['id'])
    else:
        # SQLite: usar batch mode
        op.execute("UPDATE alunos SET role = 'student' WHERE role = 'aluno'")
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
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == 'postgresql':
        op.drop_constraint('fk_alunos_mentor_id', 'alunos', type_='foreignkey')
        op.drop_column('alunos', 'mentor_id')
        op.execute("""
            CREATE TYPE role_enum_old AS ENUM ('admin', 'aluno')
        """)
        op.execute("""
            ALTER TABLE alunos
            ALTER COLUMN role TYPE role_enum_old
            USING (CASE role::text
                   WHEN 'student' THEN 'aluno'::role_enum_old
                   ELSE role::text::role_enum_old
                   END)
        """)
        op.execute("DROP TYPE role_enum")
        op.execute("ALTER TYPE role_enum_old RENAME TO role_enum")
    else:
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
