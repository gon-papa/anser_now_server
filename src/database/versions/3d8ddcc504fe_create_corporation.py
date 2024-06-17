"""create_corporation

Revision ID: 3d8ddcc504fe
Revises: f26b168b7ef3
Create Date: 2024-06-02 07:33:22.137786

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d8ddcc504fe'
down_revision: Union[str, None] = 'f26b168b7ef3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('corporations',
    sa.Column('id', sa.Integer(), nullable=False, comment='ID'),
    sa.Column('uuid', sa.String(length=36), nullable=False, comment='UUID'),
    sa.Column('name', sa.String(length=100), nullable=False, comment='企業名'),
    sa.Column('pic_name', sa.String(length=100), nullable=False, comment='企業担当者名'),
    sa.Column('pic_phone', sa.String(length=16), nullable=False, comment='企業担当者電話番号'),
    sa.Column('pic_email', sa.String(length=100), nullable=False, comment='企業担当メールアドレス'),
    sa.Column('monthly_fee', sa.Integer(), nullable=False, comment='月額利用料'),
    sa.Column('unit_price', sa.Integer(), nullable=False, comment='単価'),
    sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True, comment='削除日時'),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('uuid')
    )
    op.add_column('users', sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True, comment='削除日時'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'deleted_at')
    op.drop_table('corporations')
    # ### end Alembic commands ###
