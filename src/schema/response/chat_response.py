from datetime import datetime
from typing import List
from sqlmodel import Field, SQLModel

from src.schema.response.user_response import UserResponse
from src.schema.response.base_response import JsonResponse


class ChatIndexResponse(JsonResponse):
    class ChatIndexResponseItem(SQLModel):
        uuid: str
        user_id: int | None
        user_name: str | None
        corporation_uuid: str
        corporation_name: str
        latest_message: str
        latest_send_at: datetime
        class Config:
            from_attributes = True
            json_schema_extra = {
                "example": {
                    "uuid": "uuid",
                    "user_id": 1,
                    "corporation_uuid": "uuid",
                    "latest_message": "Hello, World!",
                    "latest_send_at": "2022-01-01 00:00:00",
                }
            }
    data: List[ChatIndexResponseItem] = Field(None, description="チャット一覧情報")
    cursor: int | None = Field(None, description="次のページのカーソル")
    
class ChatShowResponse(JsonResponse):
    class ChatShowResponseItem(SQLModel):
        uuid: str
        body: str
        send_at: datetime
        sender: int
        user: UserResponse.UserResponseItem | None
        class Config:
            from_attributes = True
            json_schema_extra = {
                "example": {
                    "uuid": "uuid",
                    "body": "Hello, World!",
                    "send_at": "2022-01-01 00:00:00",
                    "sender": 1
                }
            }
    data: List[ChatShowResponseItem] = Field(None, description="チャット詳細情報")
    cursor: int | None = Field(None, description="次のページのカーソル")
