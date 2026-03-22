"""add subtopico_area table and prerequisitos_json to topicos

Revision ID: p1q2r3s4t5u6
Revises: o1p2q3r4s5t6
Create Date: 2026-03-21

"""
from alembic import op
import sqlalchemy as sa

revision = "p1q2r3s4t5u6"
down_revision = "o1p2q3r4s5t6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Adiciona campo prerequisitos_json na tabela topicos
    op.add_column(
        "topicos",
        sa.Column("prerequisitos_json", sa.Text(), nullable=True, server_default="[]"),
    )

    # Cria tabela subtopico_areas
    op.create_table(
        "subtopico_areas",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "subtopico_id",
            sa.String(36),
            sa.ForeignKey("topicos.id"),
            nullable=False,
        ),
        sa.Column("area", sa.String(100), nullable=False),
        sa.Column("peso", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("complexidade", sa.String(10), nullable=False, server_default="media"),
        sa.UniqueConstraint("subtopico_id", "area", name="uq_subtopico_area"),
    )


def downgrade() -> None:
    op.drop_table("subtopico_areas")
    op.drop_column("topicos", "prerequisitos_json")
