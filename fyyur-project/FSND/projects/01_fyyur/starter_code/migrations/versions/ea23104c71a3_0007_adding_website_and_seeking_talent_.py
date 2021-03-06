"""0007_adding_website_and_seeking_talent_in_models

Revision ID: ea23104c71a3
Revises: cd1e36190c11
Create Date: 2021-03-01 16:33:30.803125

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea23104c71a3'
down_revision = 'cd1e36190c11'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('User', sa.Column('website', sa.String(length=120), nullable=True))
    op.add_column('Venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'seeking_talent')
    op.drop_column('User', 'website')
    # ### end Alembic commands ###
