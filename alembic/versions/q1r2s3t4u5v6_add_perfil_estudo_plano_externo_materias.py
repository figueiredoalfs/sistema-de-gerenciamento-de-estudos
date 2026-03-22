"""add tem_plano_externo and materias_selecionadas_json to perfil_estudo

Revision ID: q1r2s3t4u5v6
Revises: p1q2r3s4t5u6
Create Date: 2026-03-21

"""
from alembic import op
import sqlalchemy as sa

revision = "q1r2s3t4u5v6"
down_revision = "p1q2r3s4t5u6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "perfil_estudo",
        sa.Column("tem_plano_externo", sa.Boolean(), nullable=True, server_default="0"),
    )
    op.add_column(
        "perfil_estudo",
        sa.Column("materias_selecionadas_json", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("perfil_estudo", "materias_selecionadas_json")
    op.drop_column("perfil_estudo", "tem_plano_externo")
