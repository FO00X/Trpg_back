# Trpg_back

跑团网站后端服务，基于 **Python + FastAPI**，为前端 [Trpg_font](https://github.com/FO00X/Trpg_font)（Vue 3 + Vite）提供 HTTP API 与 Socket.IO 实时通讯。

## 技术栈

- **FastAPI**：REST 接口
- **python-socketio**：与前端 socket.io-client 同协议，同端口提供实时通讯
- **python-jose**：JWT 鉴权
- **Uvicorn**：ASGI 服务器

## 环境要求

- Python 3.8+
- 建议使用虚拟环境

## 快速开始

### 1. 克隆并进入项目

```bash
cd Trpg_back
```

### 2. 创建并激活虚拟环境

**Windows (PowerShell)：**
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS：**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 启动服务

**必须使用 `asgi_app`**，才能同时提供 HTTP API 与 Socket.IO（前端需二者同端口）：

```bash
uvicorn app.main:asgi_app --reload --port 3000
```

若未激活虚拟环境，可用模块方式启动：

```bash
python -m uvicorn app.main:asgi_app --reload --port 3000
```

启动成功后：

- **HTTP API**：<http://127.0.0.1:3000>
- **健康检查**：<http://127.0.0.1:3000/health>
- **Socket.IO**：同端口，路径 `/socket.io`；前端配置 `VITE_SOCKET_URL=http://localhost:3000` 即可。

## 项目结构

```
Trpg_back/
├── app/
│   ├── main.py              # FastAPI 应用入口，挂载路由与 Socket.IO
│   ├── routes_auth.py       # 认证：登录、当前用户
│   ├── routes_characters.py # 角色卡 CRUD
│   ├── routes_game_rooms.py # 大厅房间、模组、标签、申请加入
│   ├── routes_channels.py  # 频道列表、历史消息
│   ├── routes_rooms.py     # 旧版房间路由（可选）
│   ├── socket_io.py        # Socket.IO 事件：join、message
│   ├── channel_store.py    # 频道与消息内存存储
│   ├── realtime.py         # 原始 WebSocket 房间管理（备用）
│   └── schemas.py          # Pydantic 模型
├── docs/
│   └── API.md              # 前端对接文档（接口约定与实现状态）
├── requirements.txt
└── README.md
```

## 接口概览

| 分类   | 方法   | 路径 | 说明 |
|--------|--------|------|------|
| 认证   | POST   | `/api/auth/login` | 登录，Body：`{ "username", "password" }`，返回 `ok / token / user` |
| 认证   | GET    | `/api/auth/me` | 当前用户（需 `Authorization: Bearer <token>`） |
| 角色卡 | GET    | `/api/characters` | 当前用户角色卡列表 |
| 角色卡 | GET    | `/api/characters/:id` | 单条角色卡详情 |
| 角色卡 | POST   | `/api/characters` | 创建角色卡 |
| 角色卡 | PUT    | `/api/characters/:id` | 更新角色卡 |
| 角色卡 | DELETE | `/api/characters/:id` | 删除角色卡 |
| 大厅   | GET    | `/api/game-rooms` | 房间列表，支持 `keyword`、`status`、`module` 查询 |
| 大厅   | GET    | `/api/game-rooms/modules` | 模组列表 |
| 大厅   | GET    | `/api/game-rooms/tags` | 标签列表 |
| 大厅   | GET    | `/api/game-rooms/:id` | 房间详情 |
| 大厅   | POST   | `/api/game-rooms` | 创建房间 |
| 大厅   | POST   | `/api/game-rooms/:id/apply` | 申请加入房间 |
| 频道   | GET    | `/api/channels` | 频道列表与模组子频道 |
| 频道   | GET    | `/api/channels/:id/messages` | 历史消息，支持 `?limit=50&before=msgId` |
| 实时   | Socket.IO | `/socket.io` | 事件：`join`（传入 `channelId`）、`message`（按频道广播并落库） |

- **鉴权**：除登录外，请求头需带 `Authorization: Bearer <token>`；未登录或过期时返回 401，Body：`{ "ok": false, "message": "未登录或登录已过期" }`。
- **默认账号**（开发用）：`admin` / `123456`。

更详细的请求/响应格式、数据结构与前端约定见 **[docs/API.md](docs/API.md)**。

## 与前端联调

1. 后端在 3000 端口运行：`uvicorn app.main:asgi_app --reload --port 3000`。
2. 前端（Trpg_font）中 Vite 将 `/api` 代理到 `http://localhost:3000`，因此 `fetch('/api/auth/login', ...)` 会打到本后端。
3. 前端设置 `VITE_SOCKET_URL=http://localhost:3000`，socket.io-client 会连到本后端的 `/socket.io`。

## 数据存储说明

当前实现为**内存存储**（角色卡、大厅房间、频道消息等），进程重启后数据清空，适用于开发与联调。生产环境可接入 PostgreSQL / MySQL / Redis 等，按 [docs/API.md](docs/API.md) 中的数据结构持久化即可。

## 许可证

按项目仓库约定。
