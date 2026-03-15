"""add task_conteudo, task_videos, task_video_avaliacoes

Revision ID: i1j2k3l4m5n6
Revises: h1i2j3k4l5m6
Create Date: 2026-03-15 00:00:00.000000

Mudanças:
- Cria tabela task_conteudo (conteúdo compartilhado por subtopico+tipo)
- Cria tabela task_videos (YouTube links com avaliações)
- Cria tabela task_video_avaliacoes (nota por aluno por vídeo)
- Adiciona task_code e numero_cronograma em study_tasks
- Estende enum study_task_tipo_enum com novos tipos
"""

from alembic import op
import sqlalchemy as sa

revision = 'i1j2k3l4m5n6'
down_revision = 'h1i2j3k4l5m6'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # PostgreSQL: adicionar novos valores ao enum (SQLite ignora)
    if conn.dialect.name == "postgresql":
        for v in ["teoria", "revisao", "questionario", "simulado", "reforco"]:
            op.execute(f"ALTER TYPE study_task_tipo_enum ADD VALUE IF NOT EXISTS '{v}'")

    # 1. Criar task_conteudo
    op.create_table(
        "task_conteudo",
        sa.Column("id",           sa.String(36),  primary_key=True),
        sa.Column("task_code",    sa.String(20),  nullable=False),
        sa.Column("subtopico_id", sa.String(36),  sa.ForeignKey("topicos.id"), nullable=True),
        sa.Column("tipo",         sa.String(30),  nullable=False),
        sa.Column("objetivo",     sa.Text,        nullable=True),
        sa.Column("instrucoes",   sa.Text,        nullable=True),
        sa.Column("conteudo_pdf", sa.Text,        nullable=True),
        sa.Column("created_at",   sa.DateTime,    nullable=True),
        sa.UniqueConstraint("subtopico_id", "tipo", name="uq_task_conteudo_subtopico_tipo"),
        sa.UniqueConstraint("task_code",           name="uq_task_conteudo_task_code"),
    )
    op.create_index("ix_task_conteudo_task_code",    "task_conteudo", ["task_code"])
    op.create_index("ix_task_conteudo_subtopico_id", "task_conteudo", ["subtopico_id"])

    # 2. Criar task_videos
    op.create_table(
        "task_videos",
        sa.Column("id",               sa.String(36),  primary_key=True),
        sa.Column("task_code",        sa.String(20),  nullable=False),
        sa.Column("titulo",           sa.String(300), nullable=False),
        sa.Column("url",              sa.String(500), nullable=False),
        sa.Column("descricao",        sa.Text,        nullable=True),
        sa.Column("avaliacao_media",  sa.Float,       nullable=True, default=0.0),
        sa.Column("total_avaliacoes", sa.Integer,     nullable=True, default=0),
        sa.Column("created_at",       sa.DateTime,    nullable=True),
        sa.ForeignKeyConstraint(["task_code"], ["task_conteudo.task_code"], name="fk_task_videos_task_code"),
    )
    op.create_index("ix_task_videos_task_code", "task_videos", ["task_code"])

    # 3. Criar task_video_avaliacoes
    op.create_table(
        "task_video_avaliacoes",
        sa.Column("id",         sa.String(36), primary_key=True),
        sa.Column("video_id",   sa.String(36), nullable=False),
        sa.Column("aluno_id",   sa.String(36), nullable=False),
        sa.Column("nota",       sa.Integer,    nullable=False),
        sa.Column("created_at", sa.DateTime,   nullable=True),
        sa.ForeignKeyConstraint(["video_id"], ["task_videos.id"],  name="fk_avaliacao_video_id"),
        sa.ForeignKeyConstraint(["aluno_id"], ["alunos.id"],       name="fk_avaliacao_aluno_id"),
        sa.UniqueConstraint("video_id", "aluno_id", name="uq_avaliacao_video_aluno"),
    )
    op.create_index("ix_task_video_avaliacoes_video_id", "task_video_avaliacoes", ["video_id"])
    op.create_index("ix_task_video_avaliacoes_aluno_id", "task_video_avaliacoes", ["aluno_id"])

    # 4. Adicionar colunas em study_tasks (batch para SQLite)
    with op.batch_alter_table("study_tasks", recreate="auto") as batch_op:
        batch_op.add_column(sa.Column("task_code",         sa.String(20),  nullable=True))
        batch_op.add_column(sa.Column("numero_cronograma", sa.Integer,     nullable=True))
        batch_op.create_index("ix_study_tasks_task_code", ["task_code"])


def downgrade():
    with op.batch_alter_table("study_tasks", recreate="auto") as batch_op:
        batch_op.drop_index("ix_study_tasks_task_code")
        batch_op.drop_column("numero_cronograma")
        batch_op.drop_column("task_code")

    op.drop_index("ix_task_video_avaliacoes_aluno_id", table_name="task_video_avaliacoes")
    op.drop_index("ix_task_video_avaliacoes_video_id", table_name="task_video_avaliacoes")
    op.drop_table("task_video_avaliacoes")

    op.drop_index("ix_task_videos_task_code", table_name="task_videos")
    op.drop_table("task_videos")

    op.drop_index("ix_task_conteudo_subtopico_id", table_name="task_conteudo")
    op.drop_index("ix_task_conteudo_task_code",    table_name="task_conteudo")
    op.drop_table("task_conteudo")
