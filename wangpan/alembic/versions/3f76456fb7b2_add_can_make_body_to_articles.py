"""add can_make_body to articles

Revision ID: 3f76456fb7b2
Revises: 3cadfe817c08
Create Date: 2014-12-15 00:12:34.327454

"""

# revision identifiers, used by Alembic.
revision = '3f76456fb7b2'
down_revision = '3cadfe817c08'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('articles', sa.Column('can_make_body', sa.Boolean(),default=False))

def downgrade():
    op.drop_column('articles', 'can_make_body')

