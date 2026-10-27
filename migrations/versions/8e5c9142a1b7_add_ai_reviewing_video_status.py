"""add ai_reviewing video status

Revision ID: 8e5c9142a1b7
Revises: 7bec17136c9a
Create Date: 2026-10-27

"""
from alembic import op


revision = "8e5c9142a1b7"
down_revision = "7bec17136c9a"
branch_labels = None
depends_on = None


def upgrade():
    if op.get_bind().dialect.name == "postgresql":
        with op.get_context().autocommit_block():
            op.execute(
                "ALTER TYPE video_status "
                "ADD VALUE IF NOT EXISTS 'ai_reviewing' BEFORE 'ai_reviewed'"
            )


def downgrade():
    pass
