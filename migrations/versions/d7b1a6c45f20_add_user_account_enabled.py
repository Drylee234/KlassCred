"""add reversible account deactivation

Revision ID: d7b1a6c45f20
Revises: c913b7d4e2a1
Create Date: 2026-11-07

"""
from alembic import op
import sqlalchemy as sa


revision = "d7b1a6c45f20"
down_revision = "c913b7d4e2a1"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "account_enabled",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            )
        )


def downgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_column("account_enabled")
