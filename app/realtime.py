from __future__ import annotations

from typing import Dict, Set

from fastapi import WebSocket


class RoomConnectionManager:
    """
    简单的内存版房间连接管理器：
    - 每个 room_id 对应一个 WebSocket 连接集合
    - 提供加入 / 离开 / 广播等方法
    """

    def __init__(self) -> None:
        self.rooms: Dict[str, Set[WebSocket]] = {}

    async def connect(self, room_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.rooms.setdefault(room_id, set()).add(websocket)

    def disconnect(self, room_id: str, websocket: WebSocket) -> None:
        connections = self.rooms.get(room_id)
        if not connections:
            return
        connections.discard(websocket)
        if not connections:
            # 房间无人时清理
            self.rooms.pop(room_id, None)

    async def broadcast(self, room_id: str, message: str) -> None:
        connections = self.rooms.get(room_id, set()).copy()
        for ws in connections:
            try:
                await ws.send_text(message)
            except Exception:
                # 异常时移除连接
                self.disconnect(room_id, ws)


room_manager = RoomConnectionManager()

