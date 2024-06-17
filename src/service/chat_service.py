
from injector import inject

from src.repository.corporation_repository import CorporationRepository
from src.const.chat_const import ChatConsts
from src.model.chat_message import ChatMessages
from src.repository.chat_repository import ChatRepository


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
        keyword: str | None
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
            await self.repository.create_chat(
                uuid=chat_uuid,
                corporation_uuid=corporation.id,
                user_id=None,
            )
        
        return await self.save_chat_message(
            chat_uuid=chat_uuid,
            corporation_uuid=corporation_uuid,
            sender=ChatConsts.SENDER_GUEST,
            user_id=None,
            body=body,
        )
    
    async def save_chat_message(
        self,
        chat_uuid: str,
        corporation_uuid: str,
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
            chat_uuid=chat_uuid,
            corporation_uuid=corporation_uuid,
            sender=sender,
            user_id=user_id,
            body=body,
        )