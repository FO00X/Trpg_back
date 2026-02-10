"""
角色卡 CRUD：GET/POST/PUT/DELETE /api/characters
与前端 src/stores/characters.js 对接，当前为内存存储，后续可接数据库。
"""
import uuid
from datetime import date
from typing import Any, Dict

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from .routes_auth import get_current_user
from .schemas import Character, User

router = APIRouter(prefix="/api/characters", tags=["characters"])

# 内存存储：{ username: { character_id: character_dict } }
_characters_by_user: Dict[str, Dict[str, Dict[str, Any]]] = {}


def _today() -> str:
    return date.today().strftime("%Y-%m-%d")


@router.get("")
async def list_characters(current_user: User = Depends(get_current_user)):
    """GET /api/characters — 获取当前用户角色卡列表，需鉴权。"""
    user_list = _characters_by_user.get(current_user.username, {})
    list_ = list(user_list.values())
    return {"ok": True, "list": list_}


@router.get("/{character_id}")
async def get_character(
    character_id: str,
    current_user: User = Depends(get_current_user),
):
    """GET /api/characters/:id — 获取单条角色卡详情，需鉴权。"""
    user_list = _characters_by_user.get(current_user.username, {})
    if character_id not in user_list:
        return JSONResponse(
            status_code=404,
            content={"ok": False, "message": "角色卡不存在"},
        )
    return {"ok": True, "character": user_list[character_id]}


@router.post("")
async def create_character(
    body: Character,
    current_user: User = Depends(get_current_user),
):
    """POST /api/characters — 创建角色卡，需鉴权。Body 为完整角色表（可不含 id、updated）。"""
    character_id = str(uuid.uuid4())
    updated = _today()
    # 转为可序列化 dict，并写入 id、updated
    raw = body.model_dump(exclude_none=False)
    raw["id"] = character_id
    raw["updated"] = updated
    if current_user.username not in _characters_by_user:
        _characters_by_user[current_user.username] = {}
    _characters_by_user[current_user.username][character_id] = raw
    return {"ok": True, "id": character_id, "character": raw}


@router.put("/{character_id}")
async def update_character(
    character_id: str,
    body: Character,
    current_user: User = Depends(get_current_user),
):
    """PUT /api/characters/:id — 更新角色卡，需鉴权。Body 为完整或部分角色表。"""
    user_list = _characters_by_user.get(current_user.username, {})
    if character_id not in user_list:
        return JSONResponse(
            status_code=404,
            content={"ok": False, "message": "角色卡不存在"},
        )
    updated = _today()
    raw = body.model_dump(exclude_none=False)
    raw["id"] = character_id
    raw["updated"] = updated
    # 合并已有字段，避免漏掉未传的字段
    existing = user_list[character_id]
    for k, v in raw.items():
        if v is not None or k in ("id", "updated"):
            existing[k] = v
    existing["updated"] = updated
    return {"ok": True, "character": existing}


@router.delete("/{character_id}")
async def delete_character(
    character_id: str,
    current_user: User = Depends(get_current_user),
):
    """DELETE /api/characters/:id — 删除角色卡，需鉴权。"""
    user_list = _characters_by_user.get(current_user.username, {})
    if character_id not in user_list:
        return JSONResponse(
            status_code=404,
            content={"ok": False, "message": "角色卡不存在"},
        )
    del user_list[character_id]
    return {"ok": True}
