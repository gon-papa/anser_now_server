from datetime import datetime
from typing import List
from uuid import uuid4
from injector import inject
from sqlalchemy import desc, func
from sqlalchemy.future import select
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
    async def get_chat_by_uuid(self, uuid: str) -> Chats:
        async with self.db.get_db() as session:
            query = (
                select(Chats)
                .where(Chats.uuid == uuid)
            )
            result = await session.exec(query)
            return result.scalars().first()
        
    # chat一覧取得
    async def get_chats(
        self,
        cursor: int | None,
        limit: int,
        keyword: str | None
    ) -> List[Chats]:
        async with self.db.get_db() as session:
            # 並び替えのためにサブクエリを作成
            ChatMessagesAlias = aliased(ChatMessages)
            subquery = (
                select(ChatMessagesAlias.chat_id, func.max(ChatMessagesAlias.send_at).label('latest_send_at'))
                .group_by(ChatMessagesAlias.chat_id)
                .subquery()
            )
            if cursor is None or cursor == 0:
                query = (
                    select(Chats)
                    .join(subquery, Chats.id == subquery.c.chat_id)
                    .options(
                        joinedload(Chats.user),
                        joinedload(Chats.corporation),
                        joinedload(Chats.messages),
                    )
                    .order_by(desc(subquery.c.latest_send_at))
                    .limit(limit)
                )
            else:
                # cursorをdatetime型に変換
                cursor = datetime.fromtimestamp(cursor)
                log(cursor)
                query = (
                    select(Chats)
                    .join(subquery, Chats.id == subquery.c.chat_id)
                    .options(
                        joinedload(Chats.user),
                        joinedload(Chats.corporation),
                        joinedload(Chats.messages)
                    )
                    .order_by(desc(subquery.c.latest_send_at))
                    .where(subquery.c.latest_send_at < cursor)
                    .limit(limit)
                )
                
            if keyword:
                query = query.where(Chats.corporation.has(Corporations.name.like(f"%{keyword}%")))
            result = await session.exec(query)
            chats = result.scalars().unique().all()
            next_cursor = int(chats[-1].messages[0].send_at.timestamp()) if chats else None
            return {"chats": chats, "next_cursor": next_cursor}
        
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
        corporation_uuid: str,
        chat_uuid: str,
        sender: int,
        user_id: int | None,
        body: str
    ) -> ChatMessages:
        async with self.db.get_db() as session:
            chat = await self.get_chat_by_uuid(chat_uuid)
            if not chat:
                chat = Chats(
                    uuid=chat_uuid,
                    corporation_id=corporation_uuid,
                    started_at=datetime.now()
                )
                await session.add(chat)
                await session.commit()
                await session.refresh(chat)

            chat_id = chat.id
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
            log(chat_message)
            return chat_message