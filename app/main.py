from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .realtime import room_manager
from .routes_auth import router as auth_router
from .routes_rooms import router as rooms_router

app = FastAPI(title="TRPG Backend", description="跑团网站后端 API 与实时通讯服务")

# 允许的前端源，可以根据实际部署情况调整
origins = [
    "http://localhost:8089",  # Vite 默认端口（参考前端项目 README）
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册 HTTP 路由
app.include_router(auth_router)
app.include_router(rooms_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.websocket("/ws/rooms/{room_id}")
async def websocket_room_endpoint(websocket: WebSocket, room_id: str):
    """
    房间 WebSocket：
    - 客户端连接后发送/接收文本消息
    - 服务器负责在同一 room_id 内广播
    - message 格式建议为 JSON，前端可自行约定，如：
      { "type": "chat", "sender": "xxx", "content": "msg" }
    """
    await room_manager.connect(room_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # 这里不对数据做解析，原样广播；前端可自行设计 JSON 协议
            await room_manager.broadcast(room_id, data)
    except WebSocketDisconnect:
        room_manager.disconnect(room_id, websocket)

