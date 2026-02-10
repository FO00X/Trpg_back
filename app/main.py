import socketio
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .realtime import room_manager
from .routes_auth import router as auth_router
from .routes_channels import router as channels_router
from .routes_characters import router as characters_router
from .routes_game_rooms import router as game_rooms_router
from .routes_rooms import router as rooms_router
from .socket_io import sio

app = FastAPI(title="TRPG Backend", description="跑团网站后端 API 与实时通讯服务")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """鉴权失败 401 时统一返回 { "ok": false, "message": "..." }"""
    if exc.status_code == 401:
        return JSONResponse(
            status_code=401,
            content={"ok": False, "message": exc.detail or "未登录或登录已过期"},
        )
    raise exc

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
app.include_router(channels_router)
app.include_router(characters_router)
app.include_router(game_rooms_router)
app.include_router(rooms_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


# Socket.IO 与 FastAPI 同端口：uvicorn 应运行 asgi_app（见下方）
asgi_app = socketio.ASGIApp(sio, app)


@app.websocket("/ws/rooms/{room_id}")
async def websocket_room_endpoint(websocket: WebSocket, room_id: str):
    """
    房间 WebSocket（备用）：非 socket.io 的原始 WebSocket。
    前端若用 socket.io-client，请连接 asgi_app 的 /socket.io，并设置 VITE_SOCKET_URL=http://localhost:3000。
    """
    await room_manager.connect(room_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await room_manager.broadcast(room_id, data)
    except WebSocketDisconnect:
        room_manager.disconnect(room_id, websocket)

