

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.model.user import Users
from src.schema.response.base_response import JsonResponse
from src.core.auth import crate_user_claim, create_access_token, get_current_active_user
from src.service.auth_service import AuthService
from src.schema.response.auth_response import AuthResponse, TokenResponse
from src.schema.request.auth_request import SignInRequest, SignUpRequest
from src.schema.response.error_response import ErrorJsonResponse
from src.core.dependency import di_injector

router = APIRouter()

@router.post(
    "/sign-up",
    tags=["auth"],
    response_model=AuthResponse,
    name="サインアップ",
    description="サインアップ",
    operation_id="sign_up",
    responses={
        400: {
            "model": ErrorJsonResponse,
            "description": "Email already registered",
        },
        500: {
            "model": ErrorJsonResponse,
            "description": "Internal Server Error",
        },
    },
)
async def sign_up(request: SignUpRequest) -> AuthResponse:
    try:
        # メールアドレス重複チェック
        if await di_injector.get_class(AuthService).is_exsist_email(email=request.email):
            raise Exception("すでにメールアドレスは登録されています。")

        service: AuthService = di_injector.get_class(AuthService)
        # ユーザー登録
        user = await service.create_user(
            account_name=request.account_name,
            email=request.email,
            password=request.password
        )
        
        claim = crate_user_claim(user)
        token = create_access_token(claim)
        
        
        responseItem = AuthResponse.AuthResponseItem(
            uuid=user.uuid,
            account_name=user.account_name,
            email=user.email,
            token=token,
            refresh_token=user.refresh_token,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

        return AuthResponse(status=200, data=responseItem, message="ok")
    except Exception:
        raise
    
@router.post(
    "/sign-in",
    tags=["auth"],
    response_model=TokenResponse,
    name="サインイン",
    description="サインイン",
    operation_id="sign_in",
    responses={
        400: {
            "model": ErrorJsonResponse,
            "description": "Invalid email or password",
        },
        500: {
            "model": ErrorJsonResponse,
            "description": "Internal Server Error",
        },
    },
)
async def sign_in(request: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
    try:
        tokenData = await di_injector.get_class(AuthService).sign_in(
            email=request.username,
            password=request.password
        )
        
        return TokenResponse(
            access_token=tokenData["access_token"],
            refresh_token=tokenData["refresh_token"]
        )
    except Exception:
        raise
    
@router.post(
    "/refresh-token",
    tags=["auth"],
    response_model=TokenResponse,
    name="トークンリフレッシュ",
    description="トークンリフレッシュ",
    operation_id="refresh_token",
    responses={
        400: {
            "model": ErrorJsonResponse,
            "description": "Invalid refresh token",
        },
        500: {
            "model": ErrorJsonResponse,
            "description": "Internal Server Error",
        },
    },
)
async def refresh_token(request: TokenResponse) -> TokenResponse:
    try:
        tokenData = await di_injector.get_class(AuthService).refresh_token(
            refresh_token=request.refresh_token
        )
        
        return TokenResponse(
            access_token=tokenData["access_token"],
            refresh_token=tokenData["refresh_token"]
        )
    except Exception:
        raise
    
@router.post(
    "/sign-out",
    tags=["auth"],
    response_model=JsonResponse,
    name="サインアウト",
    description="サインアウト",
    operation_id="sign_out",
    responses={
        400: {
            "model": ErrorJsonResponse,
            "description": "Invalid refresh token",
        },
        500: {
            "model": ErrorJsonResponse,
            "description": "Internal Server Error",
        },
    },
)
async def sign_out(current_user: Users =Depends(get_current_active_user)) -> JsonResponse:
    try:
        await di_injector.get_class(AuthService).sign_out(
            user=current_user
        )
        
        return JsonResponse()
    except Exception:
        raise