import pydoc
from fastapi import HTTPException
from injector import inject

from src.core.auth import authenticate_user, crate_user_claim, create_access_token, create_expire_at, create_refresh_token, get_password_hash
from src.model.user import Users
from src.repository.user_repository import UserRepository


class AuthService:
    """AuthService
        認証サービスクラス
    """
    @inject
    def __init__(
        self,
        repository: UserRepository,
    ):
        self.repository = repository

    async def create_user(
        self,
        account_name: str,
        email: str,
        password: str,
    ) -> Users:
        """Create user

        Args:
            account_name (str): アカウント名
            email (str): メールアドレス
            password (str): パスワード

        Returns:
            Users: ユーザー情報
        """
        user = await self.create_user_object(
            account_name=account_name,
            email=email,
            password=password,
        )

        return await self.repository.create_user(user)
    
    
    async def create_user_object(
        self,
        account_name: str,
        email: str,
        password: str,
    ) -> Users:
        """Create user object

        Args:
            account_name (str): アカウント名
            email (str): メールアドレス
            password (str): パスワード

        Returns:
            Users: ユーザー情報オブジェクト
        """
        return Users(
            account_name=account_name,
            email=email,
            hashed_password=get_password_hash(password),
            is_active=True,
            refresh_token=create_refresh_token(),
            expires_at=create_expire_at(),
        )
        
    async def is_exsist_email(self, email: str) -> bool:
        """Is exsist email

        Args:
            email (str): メールアドレス

        Returns:
            bool: メールアドレスが存在するか true: 存在する false: 存在しない
        """
        user = await self.repository.get_user_by_email(email=email)
        return user is not None
    
    async def sign_in(self, email: str, password: str) -> dict:
        """sign_in

        Args:
            email (str): メールアドレス
            password (str): パスワード

        Returns:
            dict: トークン情報
        """
        user = await authenticate_user(email=email, password=password)
        if not user:
            raise HTTPException(status_code=403, detail="メールアドレスまたはパスワードが間違っています。")
        # アクセストークン作成
        claim = crate_user_claim(user)
        token = create_access_token(claim)
        # リフレッシュトークンの有効期限作成
        refresh_token = create_refresh_token()
        expires_at = create_expire_at()
        user = await self.repository.sign_in_update(user.id, refresh_token, expires_at)
        return {"access_token": token, "refresh_token": refresh_token}
    
    async def refresh_token(self, refresh_token: str) -> dict:
        """refresh_token

        Args:
            refresh_token (str): リフレッシュトークン

        Returns:
            dict: _description_
        """
        user = await self.repository.get_user_by_refresh_token(refresh_token)
        if user is None:
            raise HTTPException(status_code=403, detail="リフレッシュトークンが無効です。")
        if not user.is_active:
            raise HTTPException(status_code=400, detail="アクティブなユーザーではありません。")
        # アクセストークン作成
        claim = crate_user_claim(user)
        new_access_token = create_access_token(claim)
        # リフレッシュトークンの有効期限作成
        new_refresh_token = create_refresh_token()
        expires_at = create_expire_at()
        user = await self.repository.refresh_token_update(user.id, new_refresh_token, expires_at)  # type: ignore
        return {"access_token": new_access_token, "refresh_token": new_refresh_token}
    
    async def sign_out(self, user: Users) -> None:
        """sign_out

        Args:
            user (Users): ユーザー情報
        """
        await self.repository.sign_out_update(user)