# AI Chat - 虚拟 AI 朋友 / 智能角色聊天平台

AI Chat 是一个前后端分离的 AI 角色互动平台。用户可以注册登录、创建自己的 AI 角色、浏览他人公开的角色，并将喜欢的角色添加为"好友"进行实时聊天。项目支持文字输入、语音输入、AI 流式回复、语音播报、长期记忆和知识库检索，目标是让 AI 角色更像一个拥有设定、声音和记忆的虚拟朋友。

## 项目亮点

- **AI 角色创建**：支持角色名称、头像（含 Croppie 裁剪）、聊天背景、角色简介和音色配置。
- **角色广场与搜索**：首页按分页加载公开角色，支持按角色名、简介和作者搜索。
- **好友式聊天体验**：用户可以把角色添加为好友，进入沉浸式聊天窗口。
- **流式 AI 回复**：后端通过 SSE 返回大模型生成结果，前端边生成边展示。
- **实时语音交互**：浏览器端 VAD 语音活动检测 → 后端 ASR 语音识别 → TTS 语音合成 → 前端流式音频播放。
- **长期记忆机制**：聊天后自动总结最近对话并更新好友记忆，让角色能记住用户偏好和上下文。
- **RAG 知识库检索**：使用 LanceDB 构建向量知识库，AI 可通过工具调用检索相关内容。
- **JWT 鉴权体系**：使用 access token + refresh token，前端封装自动刷新逻辑。
- **个人资料管理**：支持用户头像、简介和账号信息维护。
- **删除确认**：移除角色或好友时弹出模态框二次确认，防止误操作。

## 快速开始

### 环境要求

- **Node.js** `^20.19.0` 或 `>=22.12.0`
- **Python** `>=3.12`
- **npm** 或 **pnpm**

### 1. 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r ../requirements.txt

# 配置环境变量（参考 .env.example）
cp .env.example .env
# 编辑 .env，填入 API_KEY 等必要配置

python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

### 2. 前端

```bash
cd frontend
npm install
# 准备 VAD 静态文件（见下方说明）
npm run dev
```

访问 `http://localhost:5173` 即可看到前端页面。

### 3. VAD 文件准备

语音功能依赖 ONNX Runtime 的 WebAssembly 文件和 Silero VAD 模型。这些文件被 `.gitignore` 忽略，需手动放入 `frontend/public/vad/`：

| 文件 | 用途 |
|------|------|
| `ort-wasm-simd-threaded.mjs` | ONNX Runtime ES module loader |
| `ort-wasm-simd-threaded.wasm` | ONNX Runtime WebAssembly |
| `ort-wasm-simd-threaded.asyncify.wasm` | ONNX Runtime (asyncify) |
| `ort-wasm-simd-threaded.jsep.wasm` | ONNX Runtime (JSEP) |
| `ort-wasm-simd-threaded.jspi.wasm` | ONNX Runtime (JSPI) |
| `silero_vad_legacy.onnx` | Silero VAD 模型 |
| `vad.worklet.bundle.min.js` | VAD Audio Worklet |

文件可通过 `npx @ricky0123/vad-web-copy <目标目录>` 获取。

### 4. 前后端联调模式

`frontend/src/js/config/config.js` 中的 `platform` 变量控制前端连接的后端地址：

| 值 | 说明 | 后端地址 |
|----|------|----------|
| `vue` | 纯前端开发模式 | `http://localhost:5173/vad/`（Vite dev server 托管 VAD 文件） |
| `django` | Django 集成开发模式 | `http://127.0.0.1:8000/static/frontend/vad/`（Django 托管静态文件） |
| `cloud` | 生产模式 | `https://xbrent.top/static/frontend/vad/` |

如果不需要语音功能，VAD 文件准备步骤可以跳过（语音功能会静默失败，不影响文字聊天）。

## 环境变量

在 `backend/.env` 中配置：

| 变量 | 说明 | 示例 |
|------|------|------|
| `API_KEY` | 大模型 API 密钥（兼容 OpenAI 接口格式） | `sk-xxx` |
| `API_BASE` | 大模型 API 地址 | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `WSS_URL` | ASR 语音识别 WebSocket 地址 | `wss://dashscope.aliyuncs.com/api-ws/v1/inference` |
| `VOICE_URL` | TTS 自定义音色服务地址 | — |
> 开发阶段默认使用 SQLite，无需配置数据库变量。

## 技术栈

### 前端

| 依赖 | 版本 | 用途 |
|------|------|------|
| Vue 3 | ^3.5 | 前端框架 |
| Vite | ^7.3 | 构建工具 |
| Vue Router | ^5.0 | 前端路由 |
| Pinia | ^3.0 | 状态管理 |
| Axios | ^1.15 | HTTP 请求 |
| @microsoft/fetch-event-source | ^2.0 | SSE 流式接收 |
| @ricky0123/vad-web | ^0.0.30 | 浏览器端 VAD 语音检测 |
| Tailwind CSS | ^4.2 | CSS 框架 |
| DaisyUI | ^5.5 | Tailwind 组件库 |
| Croppie | ^2.6 | 图片裁剪 |

### 后端

| 依赖 | 版本 | 用途 |
|------|------|------|
| Django | 6.0 | Web 框架 |
| Django REST Framework | 3.17 | REST API |
| djangorestframework-simplejwt | 5.5 | JWT 鉴权 |
| django-cors-headers | 4.9 | 跨域支持 |
| LangChain | 1.3 | AI Agent 编排 |
| LangGraph | 1.2 | 对话状态图 |
| OpenAI SDK | 2.36 | 大模型兼容接口 |
| LanceDB | 0.30 | 向量知识库 |
| Pillow | 12.2 | 图片处理 |
| python-dotenv | 1.2 | 环境变量加载 |
| psycopg2-binary | 2.9 | PostgreSQL 驱动（生产） |
| websockets | 16.0 | WebSocket（ASR） |

## 核心功能

### 1. 用户系统

项目实现了完整的用户账号流程：

- 注册账号
- 登录账号
- 退出登录
- 获取当前用户信息
- 修改个人资料（头像裁剪、简介编辑）
- 重置密码
- access token 过期后自动使用 refresh token 刷新

相关后端接口位于：

```text
backend/web/views/user/account/
backend/web/views/user/profile/
```

前端通过 Pinia 保存用户状态（`stores/user.js`），并在 Axios 拦截器中统一处理 token 刷新。

### 2. AI 角色系统

用户可以创建和管理自己的 AI 角色。每个角色包含：

- 作者
- 名称
- 头像（支持 Croppie 裁剪）
- 聊天背景图（支持 Croppie 裁剪）
- 角色设定 / 简介
- 绑定音色
- 创建时间和更新时间

角色数据模型位于：

```text
backend/web/models/character.py
```

角色相关接口包括：

- 创建角色
- 修改角色
- 删除角色（含模态框二次确认）
- 获取单个角色
- 获取当前用户创建的角色列表
- 获取可选音色列表

### 3. 首页角色广场

首页会加载所有公开角色，并支持搜索。后端接口按 `items_count` 分页返回数据，前端使用 IntersectionObserver 实现滚动加载。

主要文件：

```text
backend/web/views/homepage/index.py
frontend/src/views/homepage/HomepageIndex.vue
```

### 4. 好友与聊天系统

用户点击角色后，可以创建或获取对应的 Friend 关系。Friend 用于维护"某个用户"和"某个角色"之间的独立聊天上下文，包括长期记忆。

聊天消息会保存：

- 用户原始消息
- 发送给模型的完整上下文
- AI 回复
- token 消耗
- 创建时间

移除好友时会弹出确认模态框，防止误操作。

主要模型：

```text
backend/web/models/friend.py
```

### 5. 流式 AI 对话

后端使用 LangGraph 编排 AI Agent，支持：

- 注入系统提示词
- 注入角色设定
- 注入长期记忆
- 注入最近聊天记录
- 调用工具函数（含知识库检索）
- 流式生成回复

核心文件：

```text
backend/web/views/friend/message/chat/chat.py
backend/web/views/friend/message/chat/graph.py
```

前端通过 `fetchEventSource` 处理 SSE 数据流，在聊天窗口中实时追加 AI 回复内容。

### 6. 语音输入与语音播报

项目实现了较完整的语音交互链路：

1. 前端使用 VAD 检测用户说话开始与结束（`@ricky0123/vad-web` + ONNX Runtime）
2. 录音结束后将 PCM 音频上传到后端
3. 后端通过 WebSocket 连接阿里 DashScope 实时 ASR 服务，将音频转为文本
4. 文本作为用户消息发送给 AI
5. AI 回复时，后端同步调用 TTS 服务生成语音片段
6. 前端接收 base64 音频片段，并通过 MediaSource 流式播放

主要文件：

```text
frontend/src/components/character/chat_field/input_field/Microphone.vue
frontend/src/components/character/chat_field/input_field/InputField.vue
backend/web/views/friend/message/asr/asr.py
backend/web/views/friend/message/chat/chat.py
```

### 7. 长期记忆

每次聊天结束后，后端会根据最近对话和已有记忆调用大模型生成新的长期记忆，并保存到 Friend 表中。

主要文件：

```text
backend/web/views/friend/message/memory/update.py
backend/web/views/friend/message/memory/graph.py
```

这使得同一个用户和同一个角色之间可以拥有独立的长期互动历史。

### 8. 知识库检索

项目提供了基于 LanceDB 的向量知识库能力：

- 使用文本切分器切分知识文档
- 调用 embedding 模型生成向量
- 写入 LanceDB
- AI 对话时通过工具函数检索相关片段

主要文件：

```text
backend/web/documents/utils/insert_documents.py
backend/web/documents/utils/custom_embeddings.py
backend/web/views/friend/message/chat/graph.py
```

## API 接口

### 用户模块

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/user/account/register/` | 注册 |
| POST | `/api/user/account/login/` | 登录 |
| POST | `/api/user/account/logout/` | 退出 |
| POST | `/api/user/account/refresh_token/` | 刷新令牌 |
| GET | `/api/user/account/get_user_info/` | 获取用户信息 |
| POST | `/api/user/account/reset_password/` | 重置密码 |
| POST | `/api/user/profile/update/` | 更新个人资料 |

### 角色模块

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/create/character/create/` | 创建角色 |
| POST | `/api/create/character/update/` | 更新角色 |
| POST | `/api/create/character/remove/` | 删除角色 |
| POST | `/api/create/character/get_single/` | 获取单个角色 |
| GET | `/api/create/character/get_list/` | 获取角色列表 |
| GET | `/api/create/character/voice/get_list/` | 获取音色列表 |

### 首页 / 好友 / 聊天

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/homepage/index/` | 首页角色广场 |
| GET | `/api/friend/get_list/` | 好友列表 |
| POST | `/api/friend/get_or_create/` | 获取或创建好友关系 |
| POST | `/api/friend/remove/` | 移除好友 |
| POST | `/api/friend/message/chat/` | 流式聊天（SSE） |
| GET | `/api/friend/message/get_history/` | 聊天历史 |
| POST | `/api/friend/message/asr/asr/` | 语音识别 |

## 项目结构

```text
AIFriends/
├── backend/
│   ├── backend/                 # Django 项目配置
│   │   ├── settings.py          # 配置（DEBUG、数据库、JWT、CORS）
│   │   ├── urls.py              # 根路由
│   │   ├── wsgi.py              # WSGI 入口
│   │   └── asgi.py              # ASGI 入口
│   ├── web/                     # 主要业务应用
│   │   ├── models/              # 数据模型
│   │   │   ├── character.py     # 角色模型
│   │   │   ├── friend.py        # 好友 / 消息模型
│   │   │   └── user.py          # 用户扩展模型
│   │   ├── views/               # API 视图
│   │   │   ├── create/          # 角色 CRUD + 音色
│   │   │   ├── friend/          # 好友 / 聊天 / ASR / 记忆
│   │   │   ├── homepage/        # 首页角色广场
│   │   │   └── user/            # 注册 / 登录 / 资料
│   │   ├── documents/           # RAG 知识库 + embedding
│   │   ├── migrations/          # 数据库迁移
│   │   ├── templates/           # Django 模板入口
│   │   └── urls.py              # 业务路由
│   ├── static/frontend/         # 构建产物（gitignored）
│   │   ├── index.html
│   │   ├── assets/              # 编译后的 JS/CSS
│   │   └── vad/                 # VAD 模型文件
│   ├── media/                   # 用户上传文件
│   ├── manage.py
│   └── .env                     # 环境变量（gitignored）
├── frontend/
│   ├── src/
│   │   ├── components/          # 通用组件
│   │   │   └── character/       # 角色卡片 / 聊天 / VAD 组件
│   │   ├── views/               # 页面
│   │   │   ├── homepage/        # 首页
│   │   │   ├── friend/          # 好友列表
│   │   │   ├── create/          # 创建 / 编辑角色
│   │   │   └── user/            # 登录 / 注册 / 个人空间
│   │   ├── router/              # 前端路由
│   │   ├── stores/              # Pinia 状态管理
│   │   └── js/                  # API / 配置 / HTTP 工具
│   ├── public/vad/              # VAD 模型文件（gitignored）
│   ├── package.json
│   └── vite.config.js           # 构建输出到 ../backend/static/frontend
├── .env.example                 # 环境变量模板
├── deploy.sh                    # 一键部署脚本
├── requirements.txt             # Python 依赖
└── README.md
```

## 部署

### 前端构建

```bash
cd frontend
npm run build   # 输出到 ../backend/static/frontend/
```

Vite 会将编译后的 JS/CSS 放入 `assets/`，并复制 `public/` 下的所有文件（含 `vad/`）。

### 后端部署

使用 Gunicorn 运行：

```bash
cd backend
gunicorn backend.wsgi:application -b unix:/home/acs/AIFriends/backend/gunicorn.sock -D
```

生产环境需修改 `backend/backend/settings.py`：
- 设置 `DEBUG = False`
- 配置 PostgreSQL 数据库

### 一键部署

```bash
./deploy.sh         # 打包并上传到服务器
./deploy.sh --dry   # 预览将要上传的文件
```

脚本会将 `backend/**/*.py`、模板、静态文件和 `requirements.txt` 打包上传到服务器，排除 `__pycache__`、`.venv`、`media`、`db.sqlite3`、`.env` 和前端源码。

### Nginx 配置要点

语音功能依赖的 `.mjs` 和 `.wasm` 文件需要正确的 MIME 类型。**必须**在 Nginx 中配置：

```nginx
# /etc/nginx/mime.types 中添加：
application/javascript    mjs;
application/wasm          wasm;

# location /static/ 中添加 COOP/COEP 响应头（支持多线程 WASM 的 SharedArrayBuffer）：
location /static/ {
    alias /path/to/backend/static/;
    expires 30d;
    add_header Cross-Origin-Opener-Policy same-origin;
    add_header Cross-Origin-Embedder-Policy require-corp;
}
```

> **说明**：浏览器要求 ES module（`.mjs`）的 `Content-Type` 必须为 `application/javascript`，否则会拒绝加载。不加 COOP/COEP 头则 `SharedArrayBuffer` 不可用，多线程 WASM 初始化失败。这两个配置缺一不可，否则 VAD 语音检测功能在云端无法使用。
