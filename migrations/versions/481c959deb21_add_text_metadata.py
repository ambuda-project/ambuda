"""Add text metadata

Revision ID: 481c959deb21
Revises:
Create Date: 2022-07-17 14:31:01.779170

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "481c959deb21"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("texts", sa.Column("header", sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("texts", "header")
    # ### end Alembic commands ###
