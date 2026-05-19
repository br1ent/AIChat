# AIFriends - 虚拟 AI 朋友 / 智能角色聊天平台

AIFriends 是一个前后端分离的 AI 角色互动平台。用户可以注册登录、创建自己的 AI 角色、浏览他人公开的角色，并将喜欢的角色添加为“好友”进行实时聊天。项目支持文字输入、语音输入、AI 流式回复、语音播报、长期记忆和知识库检索，目标是让 AI 角色更像一个拥有设定、声音和记忆的虚拟朋友。

## 项目亮点

- **AI 角色创建**：支持角色名称、头像、聊天背景、角色简介和音色配置。
- **角色广场与搜索**：首页按分页加载公开角色，支持按角色名、简介和作者搜索。
- **好友式聊天体验**：用户可以把角色添加为好友，进入沉浸式聊天窗口。
- **流式 AI 回复**：后端通过 SSE 返回大模型生成结果，前端边生成边展示。
- **实时语音交互**：支持浏览器端 VAD 语音活动检测、ASR 语音识别、TTS 语音合成和前端流式音频播放。
- **长期记忆机制**：聊天后自动总结最近对话并更新好友记忆，让角色能记住用户偏好和上下文。
- **RAG 知识库检索**：使用 LanceDB 构建向量知识库，大模型可通过工具调用检索相关内容。
- **JWT 鉴权体系**：使用 access token + refresh token，前端封装自动刷新逻辑。
- **个人资料管理**：支持用户头像、简介和账号信息维护。

## 技术栈

### 前端

- Vue 3
- Vite
- Vue Router
- Pinia
- Axios
- `@microsoft/fetch-event-source`
- Tailwind CSS / DaisyUI
- `@ricky0123/vad-web`

### 后端

- Django 6
- Django REST Framework
- Simple JWT
- LangChain
- LangGraph
- OpenAI SDK 兼容接口
- LanceDB
- WebSocket
- SQLite

## 核心功能

### 1. 用户系统

项目实现了完整的用户账号流程：

- 注册账号
- 登录账号
- 退出登录
- 获取当前用户信息
- 修改个人资料
- 重置密码
- access token 过期后自动使用 refresh token 刷新

相关后端接口位于：

```text
backend/web/views/user/account/
backend/web/views/user/profile/
```

前端通过 Pinia 保存用户状态，并在 Axios 拦截器中统一处理鉴权请求。

### 2. AI 角色系统

用户可以创建和管理自己的 AI 角色。每个角色包含：

- 作者
- 名称
- 头像
- 聊天背景图
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
- 删除角色
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

用户点击角色后，可以创建或获取对应的 Friend 关系。Friend 用于维护“某个用户”和“某个角色”之间的独立聊天上下文，包括长期记忆。

聊天消息会保存：

- 用户原始消息
- 发送给模型的完整上下文
- AI 回复
- token 消耗
- 创建时间

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
- 调用工具函数
- 流式生成回复

核心文件：

```text
backend/web/views/friend/message/chat/chat.py
backend/web/views/friend/message/chat/graph.py
```

前端通过 `fetchEventSource` 处理 SSE 数据流，在聊天窗口中实时追加 AI 回复内容。

### 6. 语音输入与语音播报

项目实现了较完整的语音交互链路：

1. 前端使用 VAD 检测用户说话开始与结束。
2. 录音结束后将 PCM 音频上传到后端。
3. 后端通过 WebSocket 调用 ASR 服务，将音频转为文本。
4. 文本作为用户消息发送给 AI。
5. AI 回复时，后端同步调用 TTS 服务生成语音片段。
6. 前端接收 base64 音频片段，并通过 MediaSource 流式播放。

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

## 项目结构

```text
AIFriends/
├── backend/                    # Django 后端
│   ├── backend/                 # Django 项目配置
│   ├── web/                     # 主要业务应用
│   │   ├── models/              # 数据模型
│   │   ├── views/               # API 视图
│   │   ├── documents/           # 知识库与 embedding 工具
│   │   ├── migrations/          # 数据库迁移
│   │   └── templates/           # Django 模板入口
│   └── manage.py
├── frontend/                    # Vue 前端
│   ├── src/
│   │   ├── components/          # 通用组件
│   │   ├── views/               # 页面
│   │   ├── router/              # 前端路由
│   │   ├── stores/              # Pinia 状态管理
│   │   └── js/                  # API 与工具函数
│   ├── package.json
│   └── vite.config.js
├── requirements.txt             # Python 依赖
└── README.md
```
