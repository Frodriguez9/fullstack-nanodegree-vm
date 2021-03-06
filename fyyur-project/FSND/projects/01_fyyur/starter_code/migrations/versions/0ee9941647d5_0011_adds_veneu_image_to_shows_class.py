"""0011_adds_veneu_image_to_shows_class

Revision ID: 0ee9941647d5
Revises: 492c06179166
Create Date: 2021-03-24 15:36:27.921475

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0ee9941647d5'
down_revision = '492c06179166'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('venue_image_link', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Show', 'venue_image_link')
    # ### end Alembic commands ###
