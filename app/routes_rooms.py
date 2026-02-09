from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends

from .routes_auth import get_current_user
from .schemas import Room, User

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


@router.get("/", response_model=List[Room])
async def list_rooms(current_user: User = Depends(get_current_user)):
    """
    简单的房间列表接口，当前先返回假数据，方便前端联调。
    后续可以接真实数据库。
    """
    now = datetime.utcnow()
    return [
        Room(id=1, name="新手教学团", created_at=now),
        Room(id=2, name="高难度跑团", created_at=now),
    ]

