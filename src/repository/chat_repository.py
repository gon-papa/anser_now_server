from datetime import datetime
from typing import List
from uuid import uuid4
from injector import inject
from sqlalchemy import desc, func
from sqlalchemy.future import select
from sqlalchemy import not_, exists
from src.model.chat_reads import ChatsRead
from src.const.chat_const import ChatConsts
from src.model.corporation import Corporations
from src.core.logging import log
from src.model.chat_message import ChatMessages
from src.model.chat import Chats
from src.database.database import DatabaseConnection
from sqlalchemy.orm import joinedload, aliased

class ChatRepository:
    @inject
    def __init__(
        self,
        db: DatabaseConnection,
    ) -> None:
        self.db = db
        
    # chatをuuidで取得
    async def get_chat_by_uuid(self, uuid: str, user_id: int | None = None) -> Chats:
        async with self.db.get_db() as session:
            query = await self.get_chat_query(user_id)
            q = query['query'].where(Chats.uuid == uuid)

            result = await session.exec(q)
            return result.scalars().first()
        
    # chat一覧取得
    async def get_chats(
        self,
        cursor: int | None,
        limit: int,
        keyword: str | None,
        user_id: int | None = None,
    ) -> List[Chats]:
        async with self.db.get_db() as session:
            # 並び替えのためにサブクエリを作成
            query = await self.get_chat_query(user_id)
            if cursor is None or cursor == 0:
                q = query['query'].limit(limit)
            else:
                # cursorをdatetime型に変換
                cursor = datetime.fromtimestamp(cursor)
                q = query['query'].where(query['sub_query'].c.latest_send_at < cursor).limit(limit)
                
            if keyword:
                q = q.where(Chats.corporation.has(Corporations.name.like(f"%{keyword}%")))
            result = await session.exec(q)
            chats = result.scalars().unique().all()
            next_cursor = int(chats[-1].messages[0].send_at.timestamp()) if chats else None
            return {"chats": chats, "next_cursor": next_cursor}
        
    # chat取得クエリ
    async def get_chat_query(self, user_id: int | None = None):
        ChatMessagesAlias = aliased(ChatMessages)
        sub_query = (
            select(ChatMessagesAlias.chat_id, func.max(ChatMessagesAlias.send_at).label('latest_send_at'))
            .group_by(ChatMessagesAlias.chat_id)
            .subquery()
        )
        
        query = (
            select(Chats)
            .join(sub_query, Chats.id == sub_query.c.chat_id)
            .options(
                joinedload(Chats.user),
                joinedload(Chats.corporation),
                joinedload(Chats.messages).joinedload(ChatMessages.chat_read, innerjoin=False),
            )
            .order_by(desc(sub_query.c.latest_send_at))
        )
        
        query = query.order_by(desc(sub_query.c.latest_send_at))
        return {'query': query, 'sub_query': sub_query}
        
        
    # chat作成
    async def create_chat(
        self,
        corporation_uuid: str,
        uuid: str | None,
        user_id: int | None,
    ) -> Chats:
        async with self.db.get_db() as session:
            chat = Chats(
                uuid=uuid if uuid else str(uuid4()),
                corporation_id=corporation_uuid,
                user_id=user_id,
            )
            session.add(chat)
            await session.commit()
            await session.refresh(chat)
            chat = await session.execute(
                select(Chats)
                .options(
                    joinedload(Chats.user),
                    joinedload(Chats.corporation),
                    joinedload(Chats.messages),
                )
                .where(Chats.id == chat.id)
            )
            chat = chat.unique().scalar_one()
            log(chat)
            return chat
            
    
    # chatのメッセージ一覧取得
    async def get_chat_messages(self, chat_uuid: str, cursor: int | None, limit: int) -> List[ChatMessages]:
        async with self.db.get_db() as session:
            chat = await self.get_chat_by_uuid(chat_uuid)
            chat_id = chat.id
            
            if cursor is None or cursor == 0:
                query = (
                    select(ChatMessages)
                    .options(
                        joinedload(ChatMessages.user),
                    )
                    .where(ChatMessages.chat_id == chat_id)
                    .order_by(desc(ChatMessages.send_at))
                    .limit(limit)
                )
            else:
                cursor = datetime.fromtimestamp(cursor)
                query = (
                    select(ChatMessages)
                    .options(
                        joinedload(ChatMessages.user),
                    )
                    .where(ChatMessages.chat_id == chat_id)
                    .where(ChatMessages.send_at < cursor)
                    .order_by(desc(ChatMessages.send_at))
                    .limit(limit)
                )
            result = await session.exec(query)
            chat_messages = result.scalars().all()
            next_cursor = int(chat_messages[-1].send_at.timestamp()) if chat_messages else None
            return {"messages": chat_messages, "next_cursor": next_cursor}
        
    # chatメッセージ保存
    async def save_chat_message(
        self,
        chat_id: int,
        sender: int,
        user_id: int | None,
        body: str
    ) -> ChatMessages:
        async with self.db.get_db() as session:
            chat_message = ChatMessages(
                chat_id=chat_id,
                user_id=user_id,
                sender=sender,
                body=body,
                send_at=datetime.now()
            )
            session.add(chat_message)
            await session.commit()
            await session.refresh(chat_message)
            # userを含むchat_messageを再取得
            chat_message = await session.execute(
                select(ChatMessages)
                .options(joinedload(ChatMessages.user))
                .where(ChatMessages.id == chat_message.id)
            )
            chat_message = chat_message.scalar_one()
            return chat_message
        
    async def read_chat_message(self, chat_id: int, user_id: int) -> bool:
        async with self.db.get_db() as session:
            subquery = (
                select(ChatsRead)
                .where(ChatsRead.message_id == ChatMessages.id)
                .where(ChatsRead.user_id == user_id)
                .correlate(ChatMessages)
            )

            query = (
                select(ChatMessages.id)
                .outerjoin(ChatMessages.chat_read)
                .where(ChatMessages.chat_id == chat_id)
                .where(ChatMessages.sender == ChatConsts.SENDER_GUEST)
                .where(not_(exists(subquery)))
            )
            
            ids = await session.exec(query)
            ids = ids.scalars().all()
            for id in ids:
                chat_read = ChatsRead(
                    message_id=id,
                    user_id=user_id,
                )
                session.add(chat_read)
            await session.commit()
            return True
