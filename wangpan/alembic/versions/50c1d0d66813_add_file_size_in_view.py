"""add file_size_in_viewchrome.part2.rar

Revision ID: 50c1d0d66813
Revises: 56eba29be5d6
Create Date: 2014-12-07 18:07:09.443072

"""

# revision identifiers, used by Alembic.
revision = '50c1d0d66813'
down_revision = '56eba29be5d6'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('old_download_links', sa.Column('file_size_in_view', sa.String(50)))
    op.add_column('new_download_links', sa.Column('file_size_in_view', sa.String(50)))

def downgrade():
    op.drop_column('old_download_links', 'file_size_in_view')
    op.drop_column('new_download_links', 'file_size_in_view')