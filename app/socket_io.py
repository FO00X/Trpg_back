"""
Socket.IO 服务端：与前端 socket.io-client 对接。
前端通过 VITE_SOCKET_URL 连接（建议与 API 同域，如 http://localhost:3000）。
事件：join(channelId)、message（聊天消息，按 channelId 广播）。
"""
import socketio

# 与前端 CORS 一致
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=["http://localhost:8089", "http://localhost:3000"],
)


@sio.event
async def connect(sid, environ, auth):
    pass


@sio.event
async def disconnect(sid):
    pass


@sio.event
async def join(sid, data):
    """客户端加入频道：data = { "channelId": "general" }，用于按频道广播消息。"""
    if isinstance(data, dict) and data.get("channelId"):
        await sio.enter_room(sid, str(data["channelId"]))


@sio.event
async def message(sid, data):
    """
    客户端发聊天消息。服务端广播到同频道（channelId）所有连接，并写入历史供 GET /api/channels/:id/messages 拉取。
    """
    if not isinstance(data, dict):
        return
    channel_id = data.get("channelId") or "general"
    from .channel_store import append_message
    append_message(data)
    await sio.emit("message", data, room=channel_id)
