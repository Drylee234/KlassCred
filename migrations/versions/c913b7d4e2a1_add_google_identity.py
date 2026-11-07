"""add Google identity support

Revision ID: c913b7d4e2a1
Revises: a3f1c7d92e48
Create Date: 2026-11-07

"""
from alembic import op
import sqlalchemy as sa


revision = "c913b7d4e2a1"
down_revision = "a3f1c7d92e48"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.alter_column(
            "password_hash",
            existing_type=sa.String(length=255),
            nullable=True,
        )

    op.create_table(
        "google_identity",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("subject"),
        sa.UniqueConstraint("user_id"),
    )


def downgrade():
    op.drop_table("google_identity")
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.alter_column(
            "password_hash",
            existing_type=sa.String(length=255),
            nullable=False,
        )
