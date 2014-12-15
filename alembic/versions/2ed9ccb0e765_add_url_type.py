"""add url_type

Revision ID: 2ed9ccb0e765
Revises: d67fce46624
Create Date: 2014-12-14 11:52:30.159140

"""

# revision identifiers, used by Alembic.
revision = '2ed9ccb0e765'
down_revision = 'd67fce46624'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('old_download_links', sa.Column('url_type', sa.String(255),nullable=True))
    op.add_column('new_download_links', sa.Column('url_type', sa.String(255),nullable=True))

def downgrade():
    op.drop_column('old_download_links', 'url_type')
    op.drop_column('new_download_links', 'url_type')
