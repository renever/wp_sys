"""add file_size_unit column in old,new download link

Revision ID: 56eba29be5d6
Revises: 
Create Date: 2014-11-26 15:27:59.189475

"""

# revision identifiers, used by Alembic.
revision = '56eba29be5d6'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('old_download_links', sa.Column('file_size_unit', sa.String(20)))
    op.add_column('new_download_links', sa.Column('file_size_unit', sa.String(20)))

def downgrade():
    op.drop_column('old_download_links', 'file_size_unit')
    op.drop_column('new_download_links', 'file_size_unit')
