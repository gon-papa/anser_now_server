from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import TIMESTAMP
from sqlmodel import Field, SQLModel, Column, Integer, ForeignKey, Relationship
if TYPE_CHECKING:
    from src.model.user import Users
    from src.model.chat_message import ChatMessages

class ChatsRead(SQLModel, table=True):
    __tablename__ = "chat_reads"
    id: Optional[int] = Field(default=None, sa_column=Column(Integer, primary_key=True, comment="ID"))
    user_id: int = Field(sa_column=Column(Integer, ForeignKey("users.id"), nullable=True, comment="ユーザID"))
    message_id: int = Field(sa_column=Column(Integer, ForeignKey("chat_messages.id"), nullable=False, comment="企業ID"))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP(True),
            nullable=True,
            default=datetime.now(timezone.utc)
        )
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP(True),
            nullable=True,
            onupdate=datetime.now(timezone.utc)
        )
    )
    user: "Users" = Relationship(back_populates="chat_read")
    message: "ChatMessages" = Relationship(back_populates="chat_read")