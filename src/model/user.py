from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4
from sqlalchemy import TIMESTAMP
from sqlmodel import Field, SQLModel, Boolean, Column, Integer, String, Relationship


class Users(SQLModel, table=True):
    id: Optional[int] = Field(default=None, sa_column=Column(Integer, primary_key=True, comment="ID"))
    uuid: str = Field(
        default_factory=lambda: str(uuid4()), sa_column=Column(String(36), nullable=False, unique=True, comment="UUID")
    )
    account_name: str = Field(sa_column=Column(String(100), nullable=False, comment="アカウント名"))
    email: str = Field(sa_column=Column(String(100), nullable=False, unique=True, comment="メールアドレス"))
    hashed_password: str = Field(sa_column=Column(String(100), nullable=False, comment="パスワード"))
    is_active: bool = Field(
        sa_column=Column(
            Boolean, nullable=False, default=True, comment="アクティブフラグ True:ログイン中 False:ログアウト中"
        )
    )
    refresh_token: str = Field(sa_column=Column(String(100), nullable=True, comment="リフレッシュトークン"))
    expires_at: datetime = Field(sa_column=Column(TIMESTAMP(True), nullable=True, comment="リフレッシュトークン有効期限"))
    deleted_at: datetime = Field(sa_column=Column(TIMESTAMP(True), nullable=True, comment="削除日時"))
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
    chats: "Chats" = Relationship(back_populates="user") # type: ignore
    chat_messages: "ChatMessages" = Relationship(back_populates="user") # type: ignore