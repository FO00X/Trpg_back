"""
频道与历史消息的内存存储。
GET /api/channels 使用 channels + modules；
GET /api/channels/:id/messages 使用 _messages_by_channel；
Socket 收到 message 时调用 append_message 写入历史。
"""
from typing import Any, Dict, List, Optional

# 公共频道列表（大厅等），与前端 channels 一致
channels = [
    {"id": "general", "name": "大厅", "icon": "mdi:chat"},
]

# 模组及下属子频道，与文档 5.3 结构一致
modules = [
    {
        "id": "wangdie",
        "name": "亡蝶葬仪",
        "icon": "mdi:butterfly",
        "ownerId": "",
        "subChannels": [
            {"id": "wangdie-1", "name": "调查组", "userAccess": {}},
        ],
    },
    {
        "id": "zhivo",
        "name": "致我不灭的",
        "icon": "mdi:fire",
        "ownerId": "",
        "subChannels": [
            {"id": "zhivo-1", "name": "主线", "userAccess": {}},
        ],
    },
]

# 按 channelId 存储消息列表，每条与 Socket message 结构一致
_messages_by_channel: Dict[str, List[Dict[str, Any]]] = {}


def append_message(data: Dict[str, Any]) -> None:
    """Socket 收到 message 时调用，写入对应频道历史。"""
    channel_id = (data.get("channelId") or "general") or "general"
    if channel_id not in _messages_by_channel:
        _messages_by_channel[channel_id] = []
    # 避免直接引用，复制一份
    msg = dict(data)
    if "id" not in msg and "id" in data:
        msg["id"] = data["id"]
    _messages_by_channel[channel_id].append(msg)


def get_messages(channel_id: str, limit: int = 50, before: Optional[str] = None) -> List[Dict[str, Any]]:
    """按 channelId 取历史消息，支持 limit 与 before（msgId）分页。"""
    list_ = _messages_by_channel.get(channel_id, [])
    # 按 time 或顺序，before 表示取该 id 之前的消息
    if before:
        for i, m in enumerate(list_):
            if m.get("id") == before:
                list_ = list_[max(0, i - limit) : i]
                break
        else:
            list_ = list_[-limit:] if len(list_) > limit else list_
    else:
        list_ = list_[-limit:] if len(list_) > limit else list_
    return list_
