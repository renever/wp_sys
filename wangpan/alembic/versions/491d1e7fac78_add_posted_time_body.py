"""add posted time body

Revision ID: 491d1e7fac78
Revises: 50c1d0d66813
Create Date: 2014-12-07 22:28:05.425346

"""

# revision identifiers, used by Alembic.
revision = '491d1e7fac78'
down_revision = '50c1d0d66813'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('articles', sa.Column('pre_posted_date', sa.DateTime()))
    op.add_column('articles', sa.Column('posted_date', sa.DateTime()))
    op.add_column('articles', sa.Column('pre_body', sa.DateTime()))
    op.add_column('articles', sa.Column('body', sa.Text()))

def downgrade():
    op.drop_column('articles', sa.Column('pre_posted_date'))
    op.drop_column('articles', sa.Column('posted_date'))
    op.drop_column('articles', sa.Column('pre_body'))
    op.drop_column('articles', sa.Column('body', sa.String(512)))

