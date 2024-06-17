from datetime import datetime
from typing import Optional
from injector import inject
from sqlalchemy.future import select
from src.database.database import DatabaseConnection
from src.model.user import Users

class UserRepository:
    @inject
    def __init__(
        self,
        db: DatabaseConnection,
    ) -> None:
        self.db = db
        
    # ユーザー取得
    async def get_user(self) -> Optional[Users]:
        async with self.db.get_db() as session:
            result = await session.exec(select(Users))
            user = result.scalars().first()
            return user
        
    # uuidからユーザー取得
    async def get_user_by_uuid(self, uuid: str) -> Optional[Users]:
        async with self.db.get_db() as session:
            result = await session.exec(select(Users).where(Users.uuid == uuid))
            user = result.scalars().first()
            return user
        
    # リフレッシュトークンからユーザー取得
    async def get_user_by_refresh_token(self, refresh_token: str) -> Optional[Users]:
        async with self.db.get_db() as session:
            result = await session.exec(select(Users).where(Users.refresh_token == refresh_token))
            user = result.scalars().first()
            return user
    
    # メールアドレスからユーザー取得
    async def get_user_by_email(self, email: str) -> Optional[Users]:
        async with self.db.get_db() as session:
            result = await session.exec(select(Users).where(Users.email == email))
            user = result.scalars().first()
            return user
        
    # リフレッシュトークン更新
    async def refresh_token_update(
        self,
        userId: int,
        refresh_token: str,
        expires_at: datetime
    ) -> Users:
        async with self.db.get_db() as session:
            result = await session.exec(select(Users).where(Users.id == userId))
            user = result.scalars().first()
            user.refresh_token = refresh_token
            user.expires_at = expires_at
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
        
    # ユーザー作成
    async def create_user(self, user: Users) -> Users:
        async with self.db.get_db() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
        
    # サインイン更新
    async def sign_in_update(
        self,
        user_id: int,
        refresh_token: str,
        expires_at: datetime
    ) -> Users:
        async with self.db.get_db() as session:
            result = await session.exec(select(Users).where(Users.id == user_id))
            user = result.scalars().first()
            user.refresh_token = refresh_token
            user.expires_at = expires_at
            user.is_active = True
            await session.commit()
            await session.refresh(user)
            return user
        
    # サインアウト更新
    async def sign_out_update(
        self,
        user: Users
    ) -> Users:
        async with self.db.get_db() as session:
            user.refresh_token = None
            user.expires_at = None
            user.is_active = False
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user