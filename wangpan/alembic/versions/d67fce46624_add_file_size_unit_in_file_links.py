"""add file_size_unit in file_links

Revision ID: d67fce46624
Revises: 491d1e7fac78
Create Date: 2014-12-08 00:03:22.394361

"""

# revision identifiers, used by Alembic.
revision = 'd67fce46624'
down_revision = '491d1e7fac78'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('file_links', sa.Column('file_size_unit', sa.String(20)))

def downgrade():
    op.drop_column('file_links', 'file_size_unit')
