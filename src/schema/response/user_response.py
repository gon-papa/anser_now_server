
from datetime import datetime
from sqlmodel import Field, SQLModel

from src.schema.response.base_response import JsonResponse


class UserResponse(JsonResponse):
    class UserResponseItem(SQLModel):
        id: int
        uuid: str
        account_name: str
        email: str
        created_at: datetime
        updated_at: datetime
        class Config:
            from_attributes = True
            json_schema_extra = {
                "example": {
                    "id": 1,
                    "uuid": "uuid",
                    "account_name": "name",
                    "email": "a@a.com",
                    "created_at": "2022-01-01 00:00:00",
                    "updated_at": "2022-01-01 00:00:00",
                }
            }
    data: UserResponseItem = Field(None, description="ユーザー情報")