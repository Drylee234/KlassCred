"""add user.token_version

Revision ID: a3f1c7d92e48
Revises: 8e5c9142a1b7
Create Date: 2026-11-03

"""
from alembic import op
import sqlalchemy as sa


revision = "a3f1c7d92e48"
down_revision = "8e5c9142a1b7"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("token_version", sa.Integer(), nullable=False, server_default="0")
        )


def downgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_column("token_version")
