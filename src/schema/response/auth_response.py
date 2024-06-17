

from datetime import datetime
from pydantic import BaseModel
from sqlmodel import SQLModel, Field

from src.schema.response.base_response import JsonResponse


class AuthResponse(JsonResponse):
    class AuthResponseItem(SQLModel):
        uuid: str
        account_name: str
        email: str
        token: str
        refresh_token: str
        created_at: datetime
        updated_at: datetime
        class Config:
            from_attributes = True
            json_schema_extra = {
                "example": {
                    "uuid": "uuid",
                    "account_name": "account_name",
                    "email": "a@a.com",
                    "token": "xxxxxxx",
                    "refresh_token": "xxxxxxx",
                    "created_at": "2022-01-01 00:00:00",
                    "updated_at": "2022-01-01 00:00:00",
                }
            }
    data: AuthResponseItem = Field(None, description="ユーザー情報")
    
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str