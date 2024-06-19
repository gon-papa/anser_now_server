

import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Union

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from authlib.jose import JoseError, jwt
from authlib.jose.errors import DecodeError
from passlib.context import CryptContext

from src.core.logging import log_error
from src.core.dependency import di_injector
from src.model.user import Users
from src.repository.user_repository import UserRepository

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="sign-in")

secret_key = os.getenv("JWT_SECRET_KEY", "secret")

algorithm = "HS256"

expired_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


# パスワード比較
def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# パスワードのハッシュ化
def get_password_hash(password) -> str:
    return pwd_context.hash(password)


# リフレッシュトークン作成
def create_refresh_token() -> str:
    return secrets.token_urlsafe(64)


# リフレッシュトークンの有効期限作成
def create_expire_at() -> datetime:
    day = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAY", "30"))
    create_expire_at = datetime.now(timezone.utc) + timedelta(days=day)
    return create_expire_at


# 認証チェック
# emailとpasswordが一致するユーザーを取得
async def authenticate_user(email: str, password: str) -> Union[Users, bool]:
    repository = di_injector.get_class(UserRepository)
    user = await repository.get_user_by_email(email)
    if user is None:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


# jwtペイロード作成
def crate_user_claim(user: Users) -> dict:
    access_token_data = {
        "sub": user.uuid,  # 一意の識別子
        "aud": "user",  # role
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expired_minutes),  # 有効期限
    }
    return access_token_data


# アクセストークン作成
def create_access_token(data: dict):
    to_encode = data.copy()
    header = {"alg": algorithm, "typ": "JWT"}
    encoded_jwt = jwt.encode(header, to_encode, secret_key)
    return encoded_jwt


# アクセストークン解析
async def get_current_user(token: str = Depends(oauth2_scheme)) -> Optional[Users]:
    try:
        payload = jwt.decode(token, secret_key)
        uuid: Optional[str] = payload.get("sub")
        if uuid is None:
            credentials_exception(None)
    except JoseError as e:
        credentials_exception(e)
    user = await di_injector.get_class(UserRepository).get_user_by_uuid(uuid)
    if user is None:
        credentials_exception(None)
    return user

# websocket用アクセストークン解析
async def get_current_user_ws(token: str) -> bool:
    try:
        payload = jwt.decode(token, secret_key)
        uuid: Optional[str] = payload.get("sub")
        if uuid is None:
            credentials_exception(None)
    except Exception as e:
        credentials_exception(e)
    user = await di_injector.get_class(UserRepository).get_user_by_uuid(uuid)
    if user is None:
        credentials_exception(None)
    return True


# 解析失敗時の例外
def credentials_exception(e: Union[JoseError, None]):
    log_error(e)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証情報が無効です。",
        headers={"WWW-Authenticate": "Bearer"},
    )


# ユーザー認証
async def get_current_active_user(current_user: Users = Depends(get_current_user)) -> Users:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="アクティブなユーザーではありません。")
    return current_user