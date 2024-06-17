from fastapi import APIRouter, Depends, WebSocket
from src.schema.request.chat_request import ChatSaveMessageRequest
from src.service.corporation_service import CorporationService
from src.core.logging import log
from src.schema.response.chat_response import ChatIndexResponse, ChatShowResponse
from src.service.chat_service import ChatService
from src.core.auth import get_current_active_user
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
            keyword=keyword
        )
        chats_data = []
        for chat in chats['chats']:
            item = ChatIndexResponse.ChatIndexResponseItem(
                uuid=chat.uuid,
                user_id=chat.user_id,
                user_name=chat.user.account_name if chat.user_id else None,
                corporation_uuid=chat.corporation.uuid,
                corporation_name=chat.corporation.name,
                latest_message=chat.messages[0].body,
                latest_send_at=chat.messages[0].send_at
            )
            chats_data.append(item)
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
    "/chat/guest-message",
    tags=["chat"],
    response_model=None,
    name="ゲスト用チャットメッセージ保存",
    description="チャットメッセージを保存します。",
    operation_id="save_chat_message",
)
async def save_guest_message(request: ChatSaveMessageRequest):
    try:
        chat_message = await di_injector.get_class(ChatService).guest_save_chat_message(
            chat_uuid=request.chat_uuid,
            corporation_uuid=request.corporation_uuid,
            body=request.body
        )
        
        await room_connection_manager.broadcast(
            ChatShowResponse.ChatShowResponseItem(
                uuid=chat_message.uuid,
                body=chat_message.body,
                send_at=chat_message.send_at,
                sender=chat_message.sender,
                user=None
            ),
            request.chat_uuid,
        )
        return 'OK'
    except Exception:
        raise
    


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
        
        while True: 
            data = await websocket.receive_text()
            await room_connection_manager.broadcast(data, chat_uuid)
    except Exception:
        room_connection_manager.disconnect(websocket, chat_uuid)
        raise