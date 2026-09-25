"""verification workflow, applications, location, ai_reviewing status

Revision ID: c41d7a9e5b20
Revises: 7bec17136c9a
Create Date: 2026-09-24

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'c41d7a9e5b20'
down_revision = '7bec17136c9a'
branch_labels = None
depends_on = None


def upgrade():
    # New video_status value. ALTER TYPE ... ADD VALUE must run outside a
    # transaction block, hence autocommit_block().
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE video_status ADD VALUE IF NOT EXISTS 'ai_reviewing' BEFORE 'ai_reviewed'")

    vstatus = postgresql.ENUM('not_requested', 'pending', 'approved', 'rejected',
                              name='verification_status', create_type=False)
    vstatus.create(op.get_bind(), checkfirst=True)

    op.add_column('teacher', sa.Column('verification_status', vstatus,
                                       nullable=False, server_default='not_requested'))
    op.add_column('teacher', sa.Column('verification_rejection_reason', sa.Text(), nullable=True))
    op.add_column('teacher', sa.Column('verification_requested_at', sa.DateTime(), nullable=True))
    op.add_column('teacher', sa.Column('location', sa.String(length=255), nullable=True))
    op.add_column('teacher', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('teacher', sa.Column('longitude', sa.Float(), nullable=True))
    op.create_index('ix_teacher_verification_status', 'teacher', ['verification_status'])

    # Teachers already flagged id_verified keep their badge.
    op.execute("""UPDATE teacher SET verification_status = 'approved'
                  WHERE id IN (SELECT id FROM "user" WHERE id_verified = true)""")

    op.add_column('employer', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('employer', sa.Column('longitude', sa.Float(), nullable=True))

    op.create_table('application',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employer_id', sa.Integer(), nullable=False),
        sa.Column('teacher_id', sa.Integer(), nullable=False),
        sa.Column('position', sa.String(length=100), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'accepted', 'rejected', 'withdrawn',
                                    name='application_status'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['employer_id'], ['employer.id']),
        sa.ForeignKeyConstraint(['teacher_id'], ['teacher.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_application_employer_id', 'application', ['employer_id'])
    op.create_index('ix_application_teacher_id', 'application', ['teacher_id'])


def downgrade():
    op.drop_index('ix_application_teacher_id', table_name='application')
    op.drop_index('ix_application_employer_id', table_name='application')
    op.drop_table('application')
    sa.Enum(name='application_status').drop(op.get_bind(), checkfirst=True)

    op.drop_column('employer', 'longitude')
    op.drop_column('employer', 'latitude')

    op.drop_index('ix_teacher_verification_status', table_name='teacher')
    for col in ('longitude', 'latitude', 'location', 'verification_requested_at',
                'verification_rejection_reason', 'verification_status'):
        op.drop_column('teacher', col)
    sa.Enum(name='verification_status').drop(op.get_bind(), checkfirst=True)
    # 'ai_reviewing' stays in video_status: Postgres can't drop enum values.
