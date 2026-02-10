# 前端对接文档（FastAPI 后端实现参考）

本文档描述 TRPG 前端当前使用的数据格式与期望的 HTTP / WebSocket 接口，供 FastAPI 后端实现时对接使用。  
前端项目：Vue 3 + Vite，请求通过 Vite 代理 `/api` 到后端（开发时 `http://localhost:3000`）。

---

## 后端实现状态（TRPG_back）

当前 FastAPI 后端已按本文档实现以下部分，供前端联调与部署参考。

| 模块 | 状态 | 说明 |
|------|------|------|
| **认证** | ✅ 已实现 | `POST /api/auth/login`、`GET /api/auth/me`；401 全局统一返回 `{ ok: false, message: "未登录或登录已过期" }` |
| **角色卡** | ✅ 已实现 | `GET/POST/PUT/DELETE /api/characters`，结构与文档第三节一致；当前为内存存储，按用户分桶 |
| **大厅** | ✅ 已实现 | `GET /api/game-rooms`（keyword、status、module 查询）、`GET /api/game-rooms/modules`、`GET /api/game-rooms/tags`、`GET/POST /api/game-rooms`、`POST /api/game-rooms/:id/apply`；当前为内存存储 |
| **Socket** | ✅ 已实现 | 使用 **python-socketio**，与 FastAPI 共端口，需通过 **ASGI** 启动：`uvicorn app.main:asgi_app --reload --port 3000`。事件：**join**（客户端发 `{ channelId }` 进入频道）、**message**（客户端发消息，服务端按 channelId 广播） |
| **频道/子频道 REST** | ✅ 已实现 | `GET /api/channels` → `{ ok, channels, modules }`（含 subChannels、userAccess） |
| **历史消息** | ✅ 已实现 | `GET /api/channels/:channelId/messages?limit=50&before=msgId` → `{ ok, messages }`；Socket 收到的 message 会写入历史供拉取 |

**前端联调要点**

- 后端启动：在 `TRPG_back` 目录执行 `uvicorn app.main:asgi_app --reload --port 3000`（必须用 `asgi_app` 才能同时提供 HTTP 与 Socket）。
- Socket 同域：前端设置 `VITE_SOCKET_URL=http://localhost:3000` 即可与后端同域连接（开发时 Vite 代理只代理 `/api`，Socket 需直连 3000 或通过同一 host 访问）。

---

## 一、通用约定

### 1.1 Base URL 与 CORS

- **接口前缀**：所有 HTTP 接口建议统一为 `/api`（例如 `POST /api/auth/login`）。
- **CORS**：后端需允许前端域名（开发时为 `http://localhost:8089`，生产时为你的前端域名）跨域访问，并视需要支持 `credentials: true`（若使用 Cookie）。

### 1.2 鉴权

- 登录成功后，前端将 `token` 存入 localStorage（key：`foxtrpg-auth`），并与 `user.username` 一起保存。
- **需要鉴权的接口**：请求头中携带：
  ```http
  Authorization: Bearer <token>
  ```
- 若 token 无效或过期，建议返回 `401`，响应体建议：`{ "ok": false, "message": "未登录或登录已过期" }`。

### 1.3 统一响应结构

- **成功**：HTTP 2xx，业务成功时建议 body 含 `"ok": true`，以及具体数据字段。
- **业务失败**：可返回 4xx，body 建议：`{ "ok": false, "message": "错误说明" }`。
- 前端对 `ok` 和 `message` 会做统一处理（如登录页展示 `message`）。

---

## 二、认证接口

### 2.1 登录（已对接）

| 项目 | 说明 |
|------|------|
| **URL** | `POST /api/auth/login` |
| **请求头** | `Content-Type: application/json` |
| **请求体** | `{ "username": "string", "password": "string" }` |
| **成功响应** | HTTP 200，Body：`{ "ok": true, "token": "string", "user": { "username": "string" } }` |
| **失败响应** | HTTP 401，Body：`{ "ok": false, "message": "用户名或密码错误" }`（或其他提示） |

- 前端调用位置：`src/stores/auth.js` 的 `login()`。
- 前端仅在 `res.ok && data?.ok && data?.token && data?.user` 时视为登录成功，并写入 localStorage。

### 2.2 获取当前用户（可选）

| 项目 | 说明 |
|------|------|
| **URL** | `GET /api/auth/me` |
| **请求头** | `Authorization: Bearer <token>` |
| **成功响应** | HTTP 200，Body：`{ "ok": true, "user": { "username": "string" } }` |
| **失败响应** | HTTP 401，Body：`{ "ok": false, "message": "未登录或登录已过期" }` |

---

## 三、角色卡接口

（结构见原文档第三节：COC 7th 角色表、GET/POST/PUT/DELETE `/api/characters`。）

---

## 四、大厅（跑团房间）接口

（房间数据结构、模组/标签、GET/POST `/api/game-rooms`、`POST /api/game-rooms/:id/apply` 见原文档第四节。）

---

## 五、聊天与实时通讯（Socket）

### 5.1 Socket 连接

- 前端使用 **socket.io-client** 连接 `VITE_SOCKET_URL`。

### 5.2 事件约定

- **客户端 → 服务端**：事件名 `message`，Payload 含 `id`, `channelId`, `userId`, `userName`, `content`, `time`, `type`, `speakerRole`, `speakerNpcId`, `speakerNpcName` 等。
- **服务端 → 客户端**：事件名 `message`，同结构；前端按 `channelId` 归入频道。

### 5.3 频道与子频道 REST（已实现）

- **频道列表**：`GET /api/channels` → `{ "ok": true, "channels": [...], "modules": [...] }`
  - `channels`：大厅等公共频道；`modules`：模组及下属子频道。
- **模组/子频道结构**（与前端 `modules` 一致）：
  ```json
  {
    "id": "wangdie",
    "name": "亡蝶葬仪",
    "icon": "mdi:butterfly",
    "ownerId": "userId",
    "subChannels": [
      {
        "id": "wangdie-1",
        "name": "调查组",
        "userAccess": { "userId": "none|readonly|full" }
      }
    ]
  }
  ```
- **历史消息**：`GET /api/channels/:channelId/messages?limit=50&before=msgId` → `{ "ok": true, "messages": [...] }`，单条消息结构与 Socket `message` 一致。

---

## 六、前端调用位置速查

| 功能 | 前端文件 | 说明 |
|------|----------|------|
| 登录 | `src/stores/auth.js` | `fetch('/api/auth/login', ...)` |
| 角色卡 | `src/stores/characters.js` | 改为 API 时在此处替换为 `fetch` |
| 大厅 | `src/stores/gameRooms.js`、`GameRoomsView.vue`、`GameRoomCreateView.vue` | 改为 API 时在 store 或页面中请求 |
| Socket | `src/services/socket.js`、`src/stores/chat.js` | `VITE_SOCKET_URL` 存在则连真实 Socket；`emit('message', msg)` |

---

## 七、实现顺序建议

1. 认证 → 2. 角色卡 → 3. 大厅 → 4. Socket + 频道/历史消息 REST。

文档版本：与当前前端代码状态一致，若前端后续调整字段或接口，请同步更新本文档。
