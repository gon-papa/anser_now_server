from fastapi import APIRouter, Depends
from src.schema.response.user_response import UserResponse
from src.core.dependency import di_injector
from src.service.user_service import UserService
from src.model.user import Users
from src.core.auth import get_current_active_user
from src.schema.response.user_response import UserResponse


router = APIRouter()

@router.get(
    "/me",
    response_model=UserResponse,
    tags=["user"],
    name="ユーザー取得",
    description="ユーザー取得",
    operation_id="get_me",
)
async def me(current_user: Users =Depends(get_current_active_user)) -> UserResponse:
    try:
        result = await di_injector.get_class(UserService).get_user()
    except Exception:
        raise
    return UserResponse(data=result)