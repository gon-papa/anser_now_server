from math import log
import os
from dotenv import load_dotenv
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from uuid import uuid4

from src.service.corporation_service import CorporationService
from src.core.dependency import di_injector

router = APIRouter()
load_dotenv()

@router.get(
    "/frame-chat/{uuid}",
    response_class=HTMLResponse,
    tags=["guest"],
    name="チャットフレーム取得",
    description="チャットフレーム取得",
    operation_id="get_frame_chat",
)
async def get_frame(request: Request, uuid: str) -> HTMLResponse:
    try:
        templates = Jinja2Templates(directory="src/resource/templates")
        corporation = await di_injector.get_class(CorporationService).check_uuid(uuid=uuid)
        if not corporation:
            return HTMLResponse(content="Not Found", status_code=404)
        uuid = uuid4()
        ws_base_url = os.getenv("WS_BASE_URL")
        ws_url = f"{ws_base_url}/chat/{corporation.uuid}/{uuid}"
    except Exception:
        raise
    return templates.TemplateResponse(
        request,
        "frame.html",
        {
            "corporation_uuid": corporation.uuid,
            "chat_uuid": uuid,
            "ws_url": ws_url
        }
    )