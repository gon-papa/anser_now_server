from typing import Any, Union
from sqlmodel import Field, SQLModel


class JsonResponse(SQLModel):
    status: int = Field(200, description="ステータスコード")
    data: Any = Field(None, description="データ")
    message: Union[str, None] = Field("ok", description="メッセージ")
