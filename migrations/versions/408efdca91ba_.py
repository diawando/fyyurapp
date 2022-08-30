"""empty message

Revision ID: 408efdca91ba
Revises: 43da7de5f4ad
Create Date: 2022-08-19 14:34:44.085445

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '408efdca91ba'
down_revision = '43da7de5f4ad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('start_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('shows', 'start_time')
    # ### end Alembic commands ###