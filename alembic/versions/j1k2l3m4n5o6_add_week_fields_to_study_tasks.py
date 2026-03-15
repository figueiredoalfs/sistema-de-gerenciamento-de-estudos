"""add week_number and order_in_week to study_tasks

Revision ID: j1k2l3m4n5o6
Revises: i1j2k3l4m5n6
Create Date: 2026-03-15 00:00:00.000000

Mudanças:
- Adiciona week_number (semana do cronograma) em study_tasks
- Adiciona order_in_week (posição dentro da semana) em study_tasks
"""

from alembic import op
import sqlalchemy as sa

revision = 'j1k2l3m4n5o6'
down_revision = 'i1j2k3l4m5n6'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("study_tasks", recreate="auto") as batch_op:
        batch_op.add_column(sa.Column("week_number",   sa.Integer, nullable=True))
        batch_op.add_column(sa.Column("order_in_week", sa.Integer, nullable=True))


def downgrade():
    with op.batch_alter_table("study_tasks", recreate="auto") as batch_op:
        batch_op.drop_column("order_in_week")
        batch_op.drop_column("week_number")
