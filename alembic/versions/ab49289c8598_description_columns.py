"""description columns

Revision ID: ab49289c8598
Revises: ba59ed32d836
Create Date: 2018-11-29 22:09:37.652842

"""

# revision identifiers, used by Alembic.
revision = 'ab49289c8598'
down_revision = 'ba59ed32d836'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('beaker_cache')
    op.add_column('authcode', sa.Column('description', sa.String(length=20), nullable=True))
    op.create_unique_constraint(None, 'clients', ['id'])
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'clients', type_='unique')
    op.drop_column('authcode', 'description')
    op.create_table('beaker_cache',
    sa.Column('namespace', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('accessed', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('created', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('data', postgresql.BYTEA(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('namespace', name='beaker_cache_pkey')
    )
    # ### end Alembic commands ###