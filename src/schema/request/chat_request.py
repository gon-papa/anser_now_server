    
from pydantic import BaseModel, Field, field_validator


class ChatSaveMessageRequest(BaseModel):
    chat_uuid: str = Field(
        ...,
        title="チャットUUID",
        description="チャットUUID",
    )
    corporation_uuid: str = Field(
        ...,
        title="企業UUID",
        description="企業UUID",
    )
    body: str = Field(
        ...,
        title="メッセージ内容",
        description="メッセージ内容",
    )