from typing import List, Dict
from venv import create
from fastapi import WebSocket

from src.schema.response.chat_response import ChatIndexResponse, ChatShowResponse
from src.core.logging import log

class ConnectionManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConnectionManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """接続する

        Args:
            websocket (WebSocket): WebSocket
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """接続先から切断する

        Args:
            websocket (WebSocket): WebSocket
        """
        self.active_connections.remove(websocket)

    async def broadcast(self, message: ChatIndexResponse.ChatIndexResponseItem):
        """接続先に配信する

        Args:
            message (dict): 送信内容
        """
        for connection in self.active_connections:
            message_dict = message.model_dump()
            message_dict['latest_send_at'] = message_dict['latest_send_at'].isoformat()
            await connection.send_json(message_dict)
            
connection_manager = ConnectionManager()

class RoomConnectionManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RoomConnectionManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, chat_uuid: str):
        """接続する

        Args:
            websocket (WebSocket): WebSocket
            str (str): 部屋ID
        """
        await websocket.accept()
        if chat_uuid not in self.active_connections:
            self.active_connections[chat_uuid] = []
        self.active_connections[chat_uuid].append(websocket)

    def disconnect(self, websocket: WebSocket, chat_uuid: str):
        """接続先から切断する

        Args:
            websocket (WebSocket): WebSocket
            str (str): 部屋ID
        """
        self.active_connections[chat_uuid].remove(websocket)
        if not self.active_connections[chat_uuid]:
            del self.active_connections[chat_uuid]

    async def broadcast(self, message: ChatShowResponse.ChatShowResponseItem, chat_uuid: str):
        """接続先に配信する

        Args:
            message (dict): 送信内容
            str (str): 部屋ID
        """
        for connection in self.active_connections[chat_uuid]:
            message_dict = message.model_dump()
            message_dict['send_at'] = message_dict['send_at'].isoformat()
            if message_dict['user']:
                message_dict['user']['created_at'] = message_dict['user']['created_at'].isoformat()
                message_dict['user']['updated_at'] = message_dict['user']['updated_at'].isoformat()
            await connection.send_json(message_dict)
            
room_connection_manager = RoomConnectionManager()