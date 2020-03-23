"""empty message

Revision ID: 2fb40b723545
Revises: 67e29180206c
Create Date: 2020-03-22 22:18:32.758330

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2fb40b723545'
down_revision = '67e29180206c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('unit', schema=None) as batch_op:
        batch_op.add_column(sa.Column('avatar_l', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('avatar_m', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('avatar_raw', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('avatar_s', sa.String(length=64), nullable=True))

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'role', ['role_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('unit', schema=None) as batch_op:
        batch_op.drop_column('avatar_s')
        batch_op.drop_column('avatar_raw')
        batch_op.drop_column('avatar_m')
        batch_op.drop_column('avatar_l')

    # ### end Alembic commands ###
