"""
频道与历史消息 REST：GET /api/channels、GET /api/channels/:channelId/messages
与文档第五节「频道与子频道（可选 REST）」一致；需鉴权。
"""
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from .channel_store import channels, get_messages, modules
from .routes_auth import get_current_user
from .schemas import User

router = APIRouter(prefix="/api/channels", tags=["channels"])


@router.get("")
async def list_channels(current_user: User = Depends(get_current_user)):
    """GET /api/channels — 频道列表 + 模组及子频道。"""
    return {"ok": True, "channels": channels, "modules": modules}


@router.get("/{channel_id}/messages")
async def list_messages(
    channel_id: str,
    limit: int = 50,
    before: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """
    GET /api/channels/:channelId/messages?limit=50&before=msgId
    历史消息，单条结构与 Socket message 一致。
    """
    messages = get_messages(channel_id, limit=limit, before=before)
    return {"ok": True, "messages": messages}
