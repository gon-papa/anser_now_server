"""change_uuid_to_chats

Revision ID: 429b72f729b9
Revises: 94614a3cf24c
Create Date: 2024-06-14 09:54:04.687634

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '429b72f729b9'
down_revision: Union[str, None] = '94614a3cf24c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('chats', 'uuid',
               existing_type=mysql.VARCHAR(length=36),
               type_=sqlmodel.sql.sqltypes.AutoString(),
               comment=None,
               existing_comment='UUID',
               existing_nullable=False)
    op.drop_index('uuid', table_name='chats')
    op.drop_column('chats', 'room_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chats', sa.Column('room_id', mysql.VARCHAR(length=36), nullable=False, comment='チャットroomのID-チャットiframe取得時に生成されるID'))
    op.create_index('uuid', 'chats', ['uuid'], unique=True)
    op.alter_column('chats', 'uuid',
               existing_type=sqlmodel.sql.sqltypes.AutoString(),
               type_=mysql.VARCHAR(length=36),
               comment='UUID',
               existing_nullable=False)
    # ### end Alembic commands ###
