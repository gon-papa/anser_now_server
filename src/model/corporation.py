
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4
from sqlmodel import SQLModel, Field, Column, Integer, String, TIMESTAMP, Relationship


class Corporations(SQLModel, table=True):
    id: Optional[int] = Field(default=None, sa_column=Column(Integer, primary_key=True, comment="ID"))
    uuid: str = Field(
        default_factory=lambda: str(uuid4()), sa_column=Column(String(36), nullable=False, unique=True, comment="UUID")
    )
    name: str = Field(sa_column=Column(String(100), nullable=False, comment="企業名"))
    pic_name: str = Field(sa_column=Column(String(100), nullable=False, comment="企業担当者名"))
    pic_phone: str = Field(sa_column=Column(String(16), nullable=False, comment="企業担当者電話番号")) 
    pic_email: str = Field(sa_column=Column(String(100), nullable=False, comment="企業担当メールアドレス"))
    monthly_fee: int = Field(sa_column=Column(Integer, nullable=False, comment="月額利用料"))
    unit_price: int = Field(sa_column=Column(Integer, nullable=False, comment="単価"))
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
    chats: "Chats" = Relationship(back_populates="corporation") # type: ignore