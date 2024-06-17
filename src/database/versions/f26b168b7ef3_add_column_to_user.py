"""add_column_to_user

Revision ID: f26b168b7ef3
Revises: d8181ecb6ec8
Create Date: 2024-05-24 15:27:35.333521

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f26b168b7ef3'
down_revision: Union[str, None] = 'd8181ecb6ec8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, comment='アクティブフラグ True:ログイン中 False:ログアウト中'))
    op.add_column('users', sa.Column('refresh_token', sa.String(length=100), nullable=True, comment='リフレッシュトークン'))
    op.add_column('users', sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=True, comment='リフレッシュトークン有効期限'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'expires_at')
    op.drop_column('users', 'refresh_token')
    op.drop_column('users', 'is_active')
    # ### end Alembic commands ###