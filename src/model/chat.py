from datetime import datetime, timezone
from typing import Optional, List
from uuid import uuid4
from sqlalchemy import TIMESTAMP
from sqlmodel import Field, SQLModel, Column, Integer, String, ForeignKey, Relationship
from src.model.corporation import Corporations
from src.model.user import Users
from src.model.chat_message import ChatMessages


class Chats(SQLModel, table=True):
    id: Optional[int] = Field(default=None, sa_column=Column(Integer, primary_key=True, comment="ID"))
    uuid: str = Field(
        Field(sa_column=Column(String(36), nullable=False, comment="UUID uuidが先行で作成されるので自動生成はしない"))
    )
    user_id: int = Field(sa_column=Column(Integer, ForeignKey("users.id"), nullable=True, comment="ユーザID"))
    corporation_id: int = Field(sa_column=Column(Integer, ForeignKey("corporations.id"), nullable=False, comment="企業ID"))
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
    user: Users = Relationship(back_populates="chats")
    corporation: Corporations = Relationship(back_populates="chats")
    messages: List[ChatMessages] = Relationship(back_populates="chat") # type: ignore