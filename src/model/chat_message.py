from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4
from sqlalchemy import TIMESTAMP
from sqlmodel import Field, SQLModel, Column, Integer, String, Text, ForeignKey, Relationship

class ChatMessages(SQLModel, table=True):
    __tablename__ = "chat_messages"
    id: Optional[int] = Field(default=None, sa_column=Column(Integer, primary_key=True, comment="ID"))
    uuid: str = Field(
        default_factory=lambda: str(uuid4()), sa_column=Column(String(36), nullable=False, unique=True, comment="UUID")
    )
    chat_id: int = Field(sa_column=Column(Integer, ForeignKey("chats.id"), nullable=False, comment="チャットID"))
    user_id: int = Field(sa_column=Column(Integer, ForeignKey("users.id"), nullable=True, comment="ユーザID"))
    sender: int = Field(sa_column=Column(Integer, nullable=False, comment="送信者 1:チャット質問者 2:企業回答者(ユーザー)"))
    body: str = Field(sa_column=Column(Text, nullable=False, comment="メッセージ内容"))
    send_at: datetime = Field(sa_column=Column(TIMESTAMP(True), nullable=False, comment="送信日時"))
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
    chat: "Chats" = Relationship(back_populates="messages") # type: ignore
    user: "Users" = Relationship(back_populates="chat_messages") # type: ignore