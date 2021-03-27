"""0002_fixing_cascade_on_delete

Revision ID: 0ca68c620f48
Revises: 5bd9e1f193e8
Create Date: 2021-02-09 12:50:32.332692

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0ca68c620f48'
down_revision = '5bd9e1f193e8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('Artist_user_id_fkey', 'Artist', type_='foreignkey')
    op.create_foreign_key(None, 'Artist', 'User', ['user_id'], ['id'], ondelete='cascade')
    op.drop_constraint('Genre_name_key', 'Genre', type_='unique')
    op.drop_constraint('Venue_user_id_fkey', 'Venue', type_='foreignkey')
    op.create_foreign_key(None, 'Venue', 'User', ['user_id'], ['id'], ondelete='cascade')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Venue', type_='foreignkey')
    op.create_foreign_key('Venue_user_id_fkey', 'Venue', 'User', ['user_id'], ['id'])
    op.create_unique_constraint('Genre_name_key', 'Genre', ['name'])
    op.drop_constraint(None, 'Artist', type_='foreignkey')
    op.create_foreign_key('Artist_user_id_fkey', 'Artist', 'User', ['user_id'], ['id'])
    # ### end Alembic commands ###