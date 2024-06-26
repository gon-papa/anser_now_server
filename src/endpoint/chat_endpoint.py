import json
from fastapi import APIRouter, Depends, HTTPException, WebSocket
from src.schema.response.base_response import JsonResponse
from src.schema.request.chat_request import ChatReadRequest, ChatSaveMessageRequest
from src.service.corporation_service import CorporationService
from src.core.logging import log, log_error
from src.schema.response.chat_response import ChatIndexResponse, ChatShowResponse
from src.service.chat_service import ChatService
from src.core.auth import get_current_active_user, get_current_user_ws
from src.model.user import Users
from src.core.ws_connect import room_connection_manager, connection_manager
from src.core.dependency import di_injector


router = APIRouter()
room_connection_manager = room_connection_manager

@router.get(
    "/chat/index",
    response_model=ChatIndexResponse,
    tags=["chat"],
    name="チャット一覧取得",
    description="チャット一覧を取得します。",
    operation_id="get_chats",
)
async def index(
    cursor: int | None = None,
    limit: int = 20,
    keyword: str = None,
    current_user: Users =Depends(get_current_active_user)
) -> ChatIndexResponse:
    try:
        chats = await di_injector.get_class(ChatService).get_chats(
            cursor=cursor,
            limit=limit,
            keyword=keyword,
            user_id=current_user.id
        )
        chats_data =  await di_injector.get_class(ChatService).chat_response_item_mapping(
            chats=chats['chats'],
            user_id=current_user.id,
        )
        # カーソルは取得した最後のメッセージのsend_atのtimestampを返す(取得した中で一番古いもの)
        return ChatIndexResponse(data=chats_data, cursor=chats['next_cursor'])
    except Exception:
        raise
    
@router.get(
    "/chat/show/{uuid}",
    response_model=ChatShowResponse,
    tags=["chat"],
    name="チャット詳細取得",
    description="チャット詳細を取得します。",
    operation_id="get_chat_detail",
)
async def show(
    uuid: str,
    cursor: int | None = None,
    limit: int = 20,
    current_user: Users =Depends(get_current_active_user)
) -> ChatShowResponse:
    try:
        chat_details = await di_injector.get_class(ChatService).get_chat_messages(
            chat_uuid=uuid,
            cursor=cursor,
            limit=limit
        )
        chats_data = []
        for chat_detail in chat_details['messages']:
            item =ChatShowResponse.ChatShowResponseItem(
                uuid=chat_detail.uuid,
                body=chat_detail.body,
                send_at=chat_detail.send_at,
                sender=chat_detail.sender,
                user=chat_detail.user
            )
            chats_data.append(item)
        return ChatShowResponse(data=chats_data, cursor=chat_details['next_cursor'])
    except Exception:
        raise
    
@router.post(
    "/chat/message",
    tags=["chat"],
    response_model=JsonResponse,
    name="ユーザー用チャットメッセージ保存",
    description="ユーザー用チャットメッセージを保存します。",
    operation_id="save_chat_message",
)
async def save_message(
    request: ChatSaveMessageRequest,
    current_user: Users =Depends(get_current_active_user)
) -> JsonResponse:
    try:
        chat_message = await di_injector.get_class(ChatService).user_save_chat_message(
            chat_uuid=request.chat_uuid,
            corporation_uuid=request.corporation_uuid,
            user_id=current_user.id,
            body=request.body
        )
        
        return JsonResponse()
    except Exception:
        raise
    
@router.post(
    "/chat/guest-message",
    tags=["chat"],
    response_model=None,
    name="ゲスト用チャットメッセージ保存",
    description="チャットメッセージを保存します。",
    operation_id="save_guest_chat_message",
)
async def save_guest_message(request: ChatSaveMessageRequest):
    try:
        await di_injector.get_class(ChatService).guest_save_chat_message(
            chat_uuid=request.chat_uuid,
            corporation_uuid=request.corporation_uuid,
            body=request.body
        )

        return JsonResponse()
    except Exception:
        raise
    
@router.websocket(
    "/ws/chat",
    name="チャット通信",
)
async def ws_chats(
    websocket: WebSocket,
) -> dict:
    await connection_manager.connect(websocket)
    try:
        data = await websocket.receive_text()
        parsed_data = json.loads(data)
        if parsed_data['token']:
            await get_current_user_ws(parsed_data['token'])
        while True:
            data = await websocket.receive_text()
            await connection_manager.broadcast(data)
    except HTTPException as e:
        log_error(e)
        raise
    except Exception as e:
        log_error(e)
        raise
    finally:
        connection_manager.disconnect(websocket)
    


@router.websocket(
    "/ws/chat/{corporation_uuid}/{chat_uuid}",
    name="チャット詳細ws通信",
)
async def ws_message(
    websocket: WebSocket,
    corporation_uuid: str,
    chat_uuid: str,
) -> dict:
    try:
        # 初回処理
        is_exisit = await di_injector.get_class(CorporationService).check_uuid(uuid=corporation_uuid)
        if not is_exisit:
            raise # 法人が存在しない場合はエラー

        # ここから通信処理
        await room_connection_manager.connect(websocket, chat_uuid)
        
        log(room_connection_manager.active_connections)
        while True: 
            data = await websocket.receive_text()
            await room_connection_manager.broadcast(data, chat_uuid)
    except Exception:
        room_connection_manager.disconnect(websocket, chat_uuid)
        raise
    
@router.post(
    "/chat/read",
    tags=["chat"],
    response_model=JsonResponse,
    name="チャット既読処理",
    description="チャットメッセージを既読にします。",
    operation_id="read_chat_message",
)
async def read_message(
    request: ChatReadRequest,
    current_user: Users =Depends(get_current_active_user)
) -> JsonResponse:
    try:
        chat = await di_injector.get_class(ChatService).read_chat_message(
            chat_uuid=request.chat_uuid,
            user_id=current_user.id
        )

        return JsonResponse()
    except Exception:
        raise