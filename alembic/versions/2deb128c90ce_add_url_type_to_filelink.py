"""add url_type to FileLink

Revision ID: 2deb128c90ce
Revises: 2ed9ccb0e765
Create Date: 2014-12-14 12:00:29.189362

"""

# revision identifiers, used by Alembic.
revision = '2deb128c90ce'
down_revision = '2ed9ccb0e765'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('file_links', sa.Column('url_type', sa.String(255),nullable=True))

def downgrade():
    op.drop_column('file_links', 'url_type')

