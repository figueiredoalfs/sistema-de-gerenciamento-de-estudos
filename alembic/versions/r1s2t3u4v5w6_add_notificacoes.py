"""add notificacoes table

Revision ID: r1s2t3u4v5w6
Revises: q1r2s3t4u5v6
Create Date: 2026-03-21

"""
from alembic import op
import sqlalchemy as sa

revision = "r1s2t3u4v5w6"
down_revision = "q1r2s3t4u5v6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "notificacoes" not in inspector.get_table_names():
        op.create_table(
            "notificacoes",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("titulo", sa.String(200), nullable=False),
            sa.Column("mensagem", sa.Text(), nullable=False),
            sa.Column("tipo", sa.String(30), nullable=False, server_default="info"),
            sa.Column("lida", sa.Boolean(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(), nullable=True),
        )


def downgrade() -> None:
    op.drop_table("notificacoes")
