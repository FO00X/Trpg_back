"""
大厅（跑团房间）接口：GET/POST /api/game-rooms、申请加入、modules/tags
与前端 src/stores/gameRooms.js、GameRoomsView、GameRoomCreateView 对接。
当前为内存存储。
"""
import uuid
from datetime import date
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from .routes_auth import get_current_user
from .schemas import GameRoom, GameRoomCreate, User

router = APIRouter(prefix="/api/game-rooms", tags=["game-rooms"])

# 房间存储：id -> room dict
_rooms: Dict[str, Dict[str, Any]] = {}

# 前端文档中的模组与标签（可后续改为后端配置或数据库）
AVAILABLE_MODULES = [
    {"id": "wangdie", "name": "亡蝶葬仪", "icon": "mdi:butterfly"},
    {"id": "zhivo", "name": "致我不灭的", "icon": "mdi:fire"},
    {"id": "custom", "name": "自定义模组", "icon": "mdi:file-document-edit"},
]
AVAILABLE_TAGS = ["恐怖", "调查", "COC", "克苏鲁", "新手向", "长团", "短团"]


def _today() -> str:
    return date.today().strftime("%Y-%m-%d")


@router.get("/modules")
async def get_modules(current_user: User = Depends(get_current_user)):
    """GET /api/game-rooms/modules — 创建房间时的模组列表。"""
    return {"ok": True, "modules": AVAILABLE_MODULES}


@router.get("/tags")
async def get_tags(current_user: User = Depends(get_current_user)):
    """GET /api/game-rooms/tags — 创建房间时的标签列表。"""
    return {"ok": True, "tags": AVAILABLE_TAGS}


@router.get("")
async def list_rooms(
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    module: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """
    GET /api/game-rooms
    查询参数：keyword（搜索）、status（逗号分隔 recruiting,full,started）、module（模组 id 或名称）
    """
    list_ = list(_rooms.values())
    if keyword:
        k = keyword.strip().lower()
        list_ = [
            r
            for r in list_
            if k in (r.get("name") or "").lower()
            or k in (r.get("description") or "").lower()
            or k in (r.get("owner") or "").lower()
            or k in (r.get("module") or "").lower()
        ]
    if status:
        allowed = {s.strip() for s in status.split(",") if s.strip()}
        if allowed:
            list_ = [r for r in list_ if (r.get("status") or "") in allowed]
    if module:
        m = module.strip().lower()
        list_ = [
            r
            for r in list_
            if m in (r.get("module") or "").lower()
            or m in (r.get("moduleIcon") or "").lower()
        ]
    return {"ok": True, "list": list_}


@router.get("/{room_id}")
async def get_room(
    room_id: str,
    current_user: User = Depends(get_current_user),
):
    """GET /api/game-rooms/:id — 房间详情。"""
    if room_id not in _rooms:
        return JSONResponse(
            status_code=404,
            content={"ok": False, "message": "房间不存在"},
        )
    return {"ok": True, "room": _rooms[room_id]}


@router.post("")
async def create_room(
    body: GameRoomCreate,
    current_user: User = Depends(get_current_user),
):
    """POST /api/game-rooms — 创建房间，需鉴权。房主为当前用户。"""
    room_id = str(uuid.uuid4())
    room = {
        "id": room_id,
        "name": body.name,
        "description": body.description or "",
        "module": body.module or "",
        "moduleIcon": body.moduleIcon or "",
        "owner": current_user.username,
        "maxPlayers": body.maxPlayers or 6,
        "currentPlayers": 1,
        "status": "recruiting",
        "tags": body.tags or [],
        "createdAt": _today(),
    }
    _rooms[room_id] = room
    return {"ok": True, "room": room}


@router.post("/{room_id}/apply")
async def apply_room(
    room_id: str,
    current_user: User = Depends(get_current_user),
):
    """POST /api/game-rooms/:id/apply — 申请加入房间。"""
    if room_id not in _rooms:
        return JSONResponse(
            status_code=404,
            content={"ok": False, "message": "房间不存在"},
        )
    # 简化逻辑：仅返回成功提示，实际审核可后续扩展
    return {"ok": True, "message": "已申请加入，等待 KP 审核"}
