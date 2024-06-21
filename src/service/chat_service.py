
from operator import is_
from typing import List
from injector import inject

from src.model.chat import Chats
from src.schema.response.chat_response import ChatIndexResponse, ChatShowResponse
from src.repository.corporation_repository import CorporationRepository
from src.const.chat_const import ChatConsts
from src.model.chat_message import ChatMessages
from src.repository.chat_repository import ChatRepository
from src.core.ws_connect import room_connection_manager, connection_manager
from src.core.logging import log


class ChatService:
    """ChatService
        チャットサービスクラス
    """
    @inject
    def __init__(
        self,
        repository: ChatRepository,
        corporation_repository: CorporationRepository,
    ):
        self.repository = repository
        self.corporation_repository = corporation_repository

    async def get_chats(
        self,
        cursor: int | None,
        limit: int,
        keyword: str | None,
        user_id: int | None = None,
    ) -> dict:
        """Get chats
        
        Args:
            cursor (int): 前回取得時のカーソル
            limit (int): 取得数

        Returns:
            dict: {chats: チャット一覧情報, next_cursor: 次のカーソル}
        """
        return await self.repository.get_chats(
            cursor=cursor,
            limit=limit,
            keyword=keyword,
            user_id=user_id,
        )
        
    async def get_chat_messages(self, chat_uuid: str, cursor: int | None, limit: int) -> dict:
        """Get chat messages
        
        Args:
            chat_uuid (str): チャットUUID
            cursor (int): 前回取得時のカーソル
            limit (int): 取得数

        Returns:
            dict: {message: メッセージ一覧情報, next_cursor: 次のカーソル}
        """
        return await self.repository.get_chat_messages(
            chat_uuid=chat_uuid,
            cursor=cursor,
            limit=limit,
        )
        
    async def user_save_chat_message(
        self,
        chat_uuid: str,
        corporation_uuid: str,
        user_id: int,
        body: str,
        ) -> ChatMessages:
        """User save chat message
        
        Args:
            chat_uuid (str): チャットUUID
            corporation_uuid (str): 企業UUID
            user_id (int): ユーザID
            body (str): メッセージ内容

        Returns:
            ChatMessages: チャットメッセージ
        """
        chat = await self.repository.get_chat_by_uuid(chat_uuid)
        if not chat:
            corporation = await self.corporation_repository.get_corporation_by_uuid(corporation_uuid)
            if corporation is None:
                raise Exception("企業が存在しません。")
            chat = await self.repository.create_chat(
                uuid=chat_uuid,
                corporation_uuid=corporation.id,
                user_id=user_id,
            )
        message = await self.save_chat_message(
            chat_id=chat.id,
            sender=ChatConsts.SENDER_USER,
            user_id=user_id,
            body=body,
        )
        chat = await self.repository.get_chat_by_uuid(chat_uuid, user_id)
        await self.chats_broadcast(chat)
        await self.room_message_broadcast(message, chat_uuid)
        return message
        
    async def guest_save_chat_message(
        self,
        chat_uuid: str,
        corporation_uuid: str,
        body: str
        ) -> ChatMessages:
        """Guest save chat message
        
        Args:
            chat_uuid (str): チャットUUID
            corporation_uuid (str): 企業UUID
            body (str): メッセージ内容

        Returns:
            ChatMessages: チャットメッセージ
        """
        chat = await self.repository.get_chat_by_uuid(chat_uuid)
        # まだチャットが存在しない場合は新規作成(uuidはiframeで先行生成されるためチャットがない場合がある)
        if not chat:
            corporation = await self.corporation_repository.get_corporation_by_uuid(corporation_uuid)
            if corporation is None:
                raise Exception("企業が存在しません。")
            chat = await self.repository.create_chat(
                uuid=chat_uuid,
                corporation_uuid=corporation.id,
                user_id=None,
            )
        
        message = await self.save_chat_message(
            chat_id=chat.id,
            sender=ChatConsts.SENDER_GUEST,
            user_id=None,
            body=body,
        )
        chat = await self.repository.get_chat_by_uuid(chat_uuid)
        await self.chats_broadcast(chat)
        await self.room_message_broadcast(message, chat_uuid)
        return message
    
    async def save_chat_message(
        self,
        chat_id: int,
        sender: int,
        user_id: int | None,
        body: str
        ) -> ChatMessages:
        """Save chat message
        
        Args:
            chat_uuid (str): チャットUUID
            sender (int): 送信者 1:チャット質問者 2:企業回答者(ユーザー)
            user_id (int): ユーザID
            body (str): メッセージ内容

        Returns:
            ChatMessages: チャットメッセージ
        """    
        return await self.repository.save_chat_message(
            chat_id=chat_id,
            sender=sender,
            user_id=user_id,
            body=body,
        )
        
    async def chats_broadcast(self, chats: Chats, user_id: int | None = None):
        """Chats broadcast
        
        Args:
            chats (Chats): チャット
        """
        chat = await self.chat_response_item_mapping([chats], user_id)
        await connection_manager.broadcast(
            chat[0]
        )
        
    async def room_message_broadcast(self, message: ChatMessages, chat_uuid: str):
        """Message broadcast
        
        Args:
            message (ChatMessages): メッセージ
            chat_uuid (str): チャットUUID
        """
        await room_connection_manager.broadcast(
            ChatShowResponse.ChatShowResponseItem(
                uuid=message.uuid,
                body=message.body,
                send_at=message.send_at,
                sender=message.sender,
                user=message.user
            ),
            chat_uuid,
        )
    
    async def chat_response_item_mapping(self, chats: List[Chats], user_id: int | None):
        """Chat response item mapping

        Args:
            chats (List[Chats]): _description_
            user_id (int | None): _description_

        Returns:
            List[ChatIndexResponse.ChatIndexResponseItem]
        """
        chats_data = []
        is_read = True
        for chat in chats:
            messages = [message for message in chat.messages if message.sender == ChatConsts.SENDER_GUEST]
            for message in messages:
                if not message.chat_read:
                    is_read = False
                    break
                if not any(read.user_id == user_id for read in message.chat_read):
                    is_read = False
                    break
                if user_id is None:
                    is_read = False
                    break
                is_read = True
                break
            item = ChatIndexResponse.ChatIndexResponseItem(
                uuid=chat.uuid,
                user_id=chat.user_id,
                user_name=chat.user.account_name if chat.user_id else None,
                corporation_uuid=chat.corporation.uuid,
                corporation_name=chat.corporation.name,
                latest_message=chat.messages[-1].body,
                latest_send_at=chat.messages[-1].send_at,
                is_read=is_read
            )
            chats_data.append(item)
        return chats_data
    
    async def read_chat_message(self, chat_uuid: str, user_id: int):
        """Read chat message
        
        Args:
            chat_uuid (str): チャットUUID
            user_id (int): ユーザID
        """
        chat = await self.repository.get_chat_by_uuid(chat_uuid)
        if not chat:
            raise Exception("チャットが存在しません。")
        await self.repository.read_chat_message(chat.id, user_id)
        chat = await self.repository.get_chat_by_uuid(chat_uuid)
        await self.chats_broadcast(chat, user_id)
        return chat
        