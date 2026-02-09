from datetime import datetime
from typing import Optional

from pydantic import BaseModel


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

