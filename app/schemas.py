from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    id: int
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class Room(BaseModel):
    id: int
    name: str
    created_at: datetime


class ChatMessage(BaseModel):
    room_id: str
    sender: str
    content: str
    timestamp: datetime


# ----- 角色卡（COC 7th，与前端 getDefaultSheet 对齐，允许额外字段） -----
class Character(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    updated: Optional[str] = None
    campaign: Optional[str] = None
    era: Optional[str] = None
    skillCap: Optional[int] = None
    attributesSource: Optional[str] = None
    name: Optional[str] = None
    occupation: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    currentResidence: Optional[str] = None
    birthplace: Optional[str] = None
    str: Optional[int] = None
    dex: Optional[int] = None
    siz: Optional[int] = None
    app: Optional[int] = None
    con: Optional[int] = None
    int: Optional[int] = None
    pow: Optional[int] = None
    edu: Optional[int] = None
    luc: Optional[int] = None
    hpCurrent: Optional[int] = None
    mpCurrent: Optional[int] = None
    sanCurrent: Optional[int] = None
    seriousWound: Optional[bool] = None
    unconscious: Optional[bool] = None
    dead: Optional[bool] = None
    temporaryInsanity: Optional[bool] = None
    permanentInsanity: Optional[bool] = None
    indefiniteInsanity: Optional[bool] = None
    skillRule: Optional[dict] = None
    skills: Optional[list] = None
    weapons: Optional[list] = None
    combat: Optional[dict] = None
    possessions: Optional[dict] = None
    mythos: Optional[dict] = None
    story: Optional[dict] = None
    companions: Optional[list] = None
    scenarios: Optional[list] = None


# ----- 大厅房间 -----
class GameRoom(BaseModel):
    id: str
    name: str
    description: str = ""
    module: str = ""
    moduleIcon: str = ""
    owner: str = ""
    maxPlayers: int = 6
    currentPlayers: int = 0
    status: str = "recruiting"  # recruiting | full | started
    tags: List[str] = []
    createdAt: str = ""


class GameRoomCreate(BaseModel):
    name: str
    description: str = ""
    module: str = ""
    moduleIcon: str = ""
    maxPlayers: int = 6
    tags: List[str] = []


# ----- Socket 聊天消息（与前端 message 事件 payload 一致） -----
class SocketMessage(BaseModel):
    id: Optional[str] = None
    channelId: Optional[str] = None
    userId: Optional[str] = None
    userName: Optional[str] = None
    content: Optional[str] = None
    time: Optional[int] = None
    type: Optional[str] = "text"
    speakerRole: Optional[str] = None
    speakerNpcId: Optional[str] = None
    speakerNpcName: Optional[str] = None

