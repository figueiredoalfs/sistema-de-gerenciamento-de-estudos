"""limpar_enum_tipo_task

Revision ID: 6221168b67ff
Revises: 4710bbb33a30
Create Date: 2026-03-16 00:16:32.398670

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6221168b67ff'
down_revision: Union[str, None] = '4710bbb33a30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == 'postgresql':
        # --- role_enum: admin/student/mentor → administrador/estudante/mentor ---
        op.execute("CREATE TYPE role_enum_new AS ENUM ('administrador', 'mentor', 'estudante')")
        op.execute("""
            ALTER TABLE alunos
            ALTER COLUMN role TYPE role_enum_new
            USING (CASE role::text
                   WHEN 'admin'    THEN 'administrador'::role_enum_new
                   WHEN 'student'  THEN 'estudante'::role_enum_new
                   WHEN 'mentor'   THEN 'mentor'::role_enum_new
                   ELSE 'estudante'::role_enum_new
                   END)
        """)
        op.execute("DROP TYPE role_enum")
        op.execute("ALTER TYPE role_enum_new RENAME TO role_enum")

        # --- diagnostico_pendente: tornar nullable ---
        op.alter_column('alunos', 'diagnostico_pendente', nullable=True)

        # --- study_tasks.tipo: recriar enum (em PostgreSQL já existe como enum desde d1e2f3a4b5c6) ---
        # Liberar a coluna do enum atual, dropar e recriar com novos valores
        op.execute("ALTER TABLE study_tasks ALTER COLUMN tipo TYPE VARCHAR USING tipo::text")
        op.execute("DROP TYPE IF EXISTS study_task_tipo_enum")
        op.execute("""
            CREATE TYPE study_task_tipo_enum AS ENUM
            ('diagnostico', 'teoria', 'revisao', 'questionario', 'simulado', 'reforco')
        """)
        op.execute("""
            ALTER TABLE study_tasks
            ALTER COLUMN tipo TYPE study_task_tipo_enum
            USING (CASE tipo
                   WHEN 'study'     THEN 'teoria'::study_task_tipo_enum
                   WHEN 'questions' THEN 'questionario'::study_task_tipo_enum
                   WHEN 'review'    THEN 'revisao'::study_task_tipo_enum
                   ELSE tipo::study_task_tipo_enum
                   END)
        """)
        op.drop_index('ix_study_tasks_subtopic_id', table_name='study_tasks')
        op.create_foreign_key(
            'fk_study_tasks_task_code', 'study_tasks', 'task_conteudo',
            ['task_code'], ['task_code']
        )

        # --- subtopico_estados: unique constraint (pode já existir se criada inline em k1l2m3n4o5p6) ---
        result = bind.execute(sa.text(
            "SELECT 1 FROM information_schema.table_constraints "
            "WHERE constraint_name='uq_subtopico_estado_aluno' AND table_name='subtopico_estados'"
        ))
        if not result.scalar():
            op.create_unique_constraint(
                'uq_subtopico_estado_aluno', 'subtopico_estados', ['aluno_id', 'subtopico_id']
            )

        # --- task_conteudo: recriar index como unique ---
        op.drop_constraint('uq_task_conteudo_task_code', 'task_conteudo', type_='unique')
        op.drop_index('ix_task_conteudo_task_code', table_name='task_conteudo')
        op.create_index('ix_task_conteudo_task_code', 'task_conteudo', ['task_code'], unique=True)

    else:
        # SQLite: usar batch mode (comportamento original)
        with op.batch_alter_table('alunos', schema=None) as batch_op:
            batch_op.alter_column('role',
                   existing_type=sa.VARCHAR(length=7),
                   type_=sa.Enum('administrador', 'mentor', 'estudante', name='role_enum'),
                   existing_nullable=False)
            batch_op.alter_column('diagnostico_pendente',
                   existing_type=sa.BOOLEAN(),
                   nullable=True,
                   existing_server_default=sa.text('0'))

        with op.batch_alter_table('study_tasks', schema=None) as batch_op:
            batch_op.alter_column('tipo',
                   existing_type=sa.VARCHAR(length=11),
                   type_=sa.Enum('diagnostico', 'teoria', 'revisao', 'questionario', 'simulado', 'reforco', name='study_task_tipo_enum'),
                   existing_nullable=False)
            batch_op.drop_index(batch_op.f('ix_study_tasks_subtopic_id'))
            batch_op.create_foreign_key('fk_study_tasks_task_code', 'task_conteudo', ['task_code'], ['task_code'])

        with op.batch_alter_table('subtopico_estados', schema=None) as batch_op:
            batch_op.create_unique_constraint('uq_subtopico_estado_aluno', ['aluno_id', 'subtopico_id'])

        with op.batch_alter_table('task_conteudo', schema=None) as batch_op:
            batch_op.drop_constraint(batch_op.f('uq_task_conteudo_task_code'), type_='unique')
            batch_op.drop_index(batch_op.f('ix_task_conteudo_task_code'))
            batch_op.create_index(batch_op.f('ix_task_conteudo_task_code'), ['task_code'], unique=True)


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == 'postgresql':
        op.drop_index('ix_task_conteudo_task_code', table_name='task_conteudo')
        op.create_index('ix_task_conteudo_task_code', 'task_conteudo', ['task_code'], unique=False)
        op.create_unique_constraint('uq_task_conteudo_task_code', 'task_conteudo', ['task_code'])

        op.drop_constraint('uq_subtopico_estado_aluno', 'subtopico_estados', type_='unique')

        op.drop_constraint('fk_study_tasks_task_code', 'study_tasks', type_='foreignkey')
        op.create_index('ix_study_tasks_subtopic_id', 'study_tasks', ['subtopic_id'], unique=False)
        op.execute("ALTER TABLE study_tasks ALTER COLUMN tipo TYPE VARCHAR(11) USING tipo::text")
        op.execute("DROP TYPE study_task_tipo_enum")

        op.alter_column('alunos', 'diagnostico_pendente', nullable=False)

        op.execute("CREATE TYPE role_enum_old AS ENUM ('admin', 'mentor', 'student')")
        op.execute("""
            ALTER TABLE alunos
            ALTER COLUMN role TYPE role_enum_old
            USING (CASE role::text
                   WHEN 'administrador' THEN 'admin'::role_enum_old
                   WHEN 'estudante'     THEN 'student'::role_enum_old
                   WHEN 'mentor'        THEN 'mentor'::role_enum_old
                   ELSE 'student'::role_enum_old
                   END)
        """)
        op.execute("DROP TYPE role_enum")
        op.execute("ALTER TYPE role_enum_old RENAME TO role_enum")

    else:
        with op.batch_alter_table('task_conteudo', schema=None) as batch_op:
            batch_op.drop_index(batch_op.f('ix_task_conteudo_task_code'))
            batch_op.create_index(batch_op.f('ix_task_conteudo_task_code'), ['task_code'], unique=False)
            batch_op.create_unique_constraint(batch_op.f('uq_task_conteudo_task_code'), ['task_code'])

        with op.batch_alter_table('subtopico_estados', schema=None) as batch_op:
            batch_op.drop_constraint('uq_subtopico_estado_aluno', type_='unique')

        with op.batch_alter_table('study_tasks', schema=None) as batch_op:
            batch_op.drop_constraint('fk_study_tasks_task_code', type_='foreignkey')
            batch_op.create_index(batch_op.f('ix_study_tasks_subtopic_id'), ['subtopic_id'], unique=False)
            batch_op.alter_column('tipo',
                   existing_type=sa.Enum('diagnostico', 'teoria', 'revisao', 'questionario', 'simulado', 'reforco', name='study_task_tipo_enum'),
                   type_=sa.VARCHAR(length=11),
                   existing_nullable=False)

        with op.batch_alter_table('alunos', schema=None) as batch_op:
            batch_op.alter_column('diagnostico_pendente',
                   existing_type=sa.BOOLEAN(),
                   nullable=False,
                   existing_server_default=sa.text('0'))
            batch_op.alter_column('role',
                   existing_type=sa.Enum('administrador', 'mentor', 'estudante', name='role_enum'),
                   type_=sa.VARCHAR(length=7),
                   existing_nullable=False)
