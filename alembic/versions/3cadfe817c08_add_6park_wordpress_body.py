"""add 6park wordpress body

Revision ID: 3cadfe817c08
Revises: 2deb128c90ce
Create Date: 2014-12-14 23:57:48.292946

"""

# revision identifiers, used by Alembic.
revision = '3cadfe817c08'
down_revision = '2deb128c90ce'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa



def upgrade():
    op.add_column('articles', sa.Column('body_6park', sa.Text,nullable=True))
    op.add_column('articles', sa.Column('body_wordpress', sa.Text,nullable=True))

def downgrade():
    op.drop_column('articles', 'body_6park')
    op.drop_column('articles', 'body_wordpress')

