# 小红书内容分析工具

本项目旨在提供一个便捷的工具，帮助用户抓取指定小红书博主的笔记内容，并对视频笔记进行文案提取和内容分析，以辅助内容创作和优化。

**重要提示：**
*   请遵守小红书平台的使用规则和相关法律法规，合理使用本工具。
*   获取和使用Cookie涉及账户安全，请妥善保管您的Cookie信息，并仅用于授权范围。

## 一、用户使用说明

本工具为不懂技术的用户设计，操作简单直观。

### 1.1 功能简介

*   **用户登录与注册**：保障您的任务数据安全。
*   **创建采集任务**：输入小红书博主主页链接、您的Cookie以及抓取规则，即可创建内容抓取任务。
*   **任务进度查看**：在工作台实时查看任务的整体进度。
*   **笔记详情与分析结果**：查看每条笔记的采集状态、原始视频/图文内容、提取的视频文案以及AI分析结果。

### 1.2 准备工作

在使用本工具前，您需要准备：

1.  **小红书账号的Cookie**：
    *   Cookie是您访问小红书的身份凭证。
    *   推荐使用浏览器插件 [CookieTool](https://github.com/wenterwang/CookieTool) 来获取。安装插件后，登录小红书网页版，点击插件图标 -> Get Cookies即可复制Cookie。
    *   **请注意**：Cookie具有时效性，如果长时间未使用或密码更改等，可能需要重新获取。
2.  **AI服务API Key**（可选，但核心分析功能需要）：
    *   本工具使用AI服务进行视频文案提取和内容分析。您需要在 `docker-compose.yml` 文件中配置 `AI_API_KEY`。
    *   API Key获取地址：[https://docs.aihubmax.com/guides/base/get-token](https://docs.aihubmax.com/guides/base/get-token)
    *   如果您不配置此项，视频文案提取和AI分析功能将无法使用。

### 1.3 如何运行工具

本工具通过Docker运行，您无需关心复杂的环境配置。

1.  **确保已安装 Docker 和 Docker Compose**：
    *   Docker Desktop (Windows/Mac): [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
    *   Docker Engine & Docker Compose (Linux): 请参照官方文档安装。
2.  **获取项目文件**：将项目文件夹下载或克隆到您的本地计算机。
3.  **配置API Key (重要)**：
    *   打开项目根目录下的 `docker-compose.yml` 文件。
    *   找到 `backend` 服务下的 `environment` 部分。
    *   修改 `AI_API_KEY: "您的 AI Hu Max API Key"`，将其中的 `"您的 AI Hu Max API Key"` 替换为您自己真实的API Key。
    *   如果您有自己的小红书API Token (非必需，工具主要依赖Cookie)，也可以配置 `XHS_API_TOKEN`。
4.  **启动服务**：
    *   打开终端 (Terminal) 或命令提示符 (Command Prompt)。
    *   进入到项目根目录 (即包含 `docker-compose.yml` 文件的目录)。
    *   运行命令：`docker-compose up -d --build`
    *   这个命令会先构建项目镜像，然后启动所有服务。首次构建可能需要一些时间。
5.  **访问工具**：
    *   启动成功后，在您的浏览器中打开 `http://localhost` (或 `http://127.0.0.1`) 即可访问工具页面。

### 1.4 使用步骤

1.  **注册与登录**：
    *   首次使用请点击“注册”按钮，创建您的账户。
    *   注册成功后，使用您的用户名和密码登录。
2.  **进入工作台**：
    *   登录成功后，您将进入工作台页面。
3.  **创建采集任务**：
    *   点击“创建新任务”或类似按钮。
    *   在表单中输入：
        *   **博主主页链接**：例如 `https://www.xiaohongshu.com/user/profile/xxxxxxxxxxxx`
        *   **您的Cookie**：粘贴您获取到的小红书Cookie。
        *   **抓取规则**：
            *   **内容类型**：选择“视频”、“图文”或“全部”。
            *   **排序方式**：选择“点赞最多”或“最新发布”。
            *   **抓取数量**：希望抓取的笔记数量（例如前10条）。
    *   点击“提交”或“创建任务”。
4.  **查看任务和笔记**：
    *   任务创建后会出现在任务列表中，您可以看到任务的当前状态（如：处理中、已识别笔记、已完成、失败等）。
    *   点击任务可以查看该任务下所有已识别笔记的列表。
    *   点击具体的笔记，可以查看该笔记的详细信息：
        *   **视频/图文内容**：直接查看或播放。
        *   **视频文案**：如果笔记是视频且处理成功，这里会显示从视频语音提取的文字。
        *   **AI分析结果**：对视频文案进行的智能分析，帮助您理解内容特点和优化方向。
        *   **处理状态**：显示笔记在各个处理阶段（采集、转写、分析）的状态。

### 1.5 注意事项

*   **Cookie有效期**：如果任务长时间失败，或者提示Cookie失效，请尝试重新获取并更新任务中的Cookie（未来版本可能支持编辑任务）。
*   **API调用频率**：频繁创建大量任务可能会触发API的频率限制，请合理安排任务。
*   **网络问题**：确保您的计算机网络通畅，以便工具能够正常访问外部API。
*   **费用**：再次提醒，AI分析功能会消耗API调用次数，产生费用。

## 二、开发者文档

本文档为需要参与本项目后续开发或维护的开发者提供指引。

### 2.1 技术栈

*   **后端**：
    *   Python 3.11+
    *   FastAPI: 高性能Web框架
    *   SQLAlchemy: ORM，用于数据库交互
    *   Pydantic: 数据校验和设置管理
    *   Httpx: 异步HTTP客户端
    *   Uvicorn: ASGI服务器
*   **前端**：
    *   Vue 3 (Composition API, `<script setup>`)
    *   Vite: 前端构建工具
    *   Naive UI: UI组件库
    *   Pinia: 状态管理
    *   Axios: HTTP客户端
    *   Sass: CSS预处理器
*   **数据库**：
    *   MySQL 8.0
*   **容器化**：
    *   Docker
    *   Docker Compose
*   **Python环境管理** (本地开发推荐)：
    *   Conda

### 2.2 项目结构

```
.
├── backend/                  # 后端 FastAPI 应用
│   ├── app/                  # FastAPI 应用核心代码 (临时名称，通常为 main.py 或 app.py 所在目录)
│   │   ├── api/              # API路由
│   │   │   └── v1/
│   │   │       ├── deps.py   # 依赖项
│   │   │       └── endpoints/ # API端点模块 (tasks, users, login, etc.)
│   │   ├── core/             # 配置、核心逻辑 (如config.py, security.py)
│   │   ├── crud/             # 数据库增删改查操作
│   │   ├── db/               # 数据库会话、初始化 (base_class.py, session.py)
│   │   ├── models/           # SQLAlchemy 数据模型
│   │   ├── schemas/          # Pydantic 数据模型 (请求/响应体)
│   │   ├── services/         # 外部服务调用 (如 XHS API, AI API)
│   │   └── main.py           # FastAPI 应用入口
│   ├── Dockerfile            # 后端 Dockerfile
│   └── requirements.txt      # Python 依赖
├── frontend/                 # 前端 Vue 应用
│   ├── public/               # 静态资源
│   ├── src/                  # Vue 应用源码
│   │   ├── api/              # API 请求模块
│   │   ├── assets/           # 静态资源 (图片、样式)
│   │   ├── components/       # Vue 组件
│   │   ├── config/           # 配置文件 (如API基础路径)
│   │   ├── router/           # Vue Router 配置
│   │   ├── stores/           # Pinia 状态管理
│   │   ├── utils/            # 工具函数
│   │   ├── views/            # Vue 视图/页面
│   │   ├── App.vue           # 根组件
│   │   └── main.js           # Vue 应用入口
│   ├── Dockerfile            # 前端 Dockerfile
│   ├── nginx.conf            # Nginx 配置文件 (用于生产环境提供静态文件)
│   ├── package.json          # Node.js 项目配置
│   └── pnpm-lock.yaml        # pnpm 锁定文件 (或 yarn.lock / package-lock.json)
├── docker-compose.yml        # Docker Compose 配置文件
└── README.md                 # 项目说明文档
```

### 2.3 环境搭建与运行 (本地开发)

#### 2.3.1 后端 (FastAPI)

1.  **Conda 环境** (推荐):
    ```bash
    conda create -n redbook_analyzer python=3.11
    conda activate redbook_analyzer
    ```
2.  **安装依赖**:
    进入 `backend` 目录:
    ```bash
    cd backend
    pip install -r requirements.txt
    ```
3.  **配置环境变量**:
    *   在 `backend` 目录下创建 `.env` 文件 (此文件已被 `.gitignore` 忽略，不会提交到版本库)。
    *   内容参考 `backend/core/config.py` 中的 `Settings` 类，至少需要配置数据库连接信息和 `SECRET_KEY`，以及 `AI_API_KEY`。
        ```env
        # backend/.env 示例
        DATABASE_URL="mysql+pymysql://your_mysql_user:your_mysql_password@localhost:3306/redbook_db" # 注意本地开发时db主机和端口
        SECRET_KEY="a_very_strong_and_random_secret_key_for_jwt"
        AI_API_KEY="your_aihubmax_api_key"
        XHS_API_TOKEN="your_xhs_api_token_if_any" # 可选

        # 如果使用本地MySQL，确保数据库 redbook_db 已创建
        ```
4.  **启动开发服务器**:
    在 `backend` 目录下运行:
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    API文档将位于 `http://localhost:8000/docs`。

#### 2.3.2 前端 (Vue)

1.  **Node.js 和 pnpm/npm/yarn**:
    *   确保已安装 Node.js (推荐 LTS 版本)。
    *   项目使用 `pnpm`，如果未安装，请先安装 `npm install -g pnpm`。
2.  **安装依赖**:
    进入 `frontend` 目录:
    ```bash
    cd frontend
    pnpm install
    ```
3.  **启动开发服务器**:
    在 `frontend` 目录下运行:
    ```bash
    pnpm dev
    ```
    前端页面通常会运行在 `http://localhost:5173` (Vite 默认端口，具体看终端输出)。
    开发服务器会自动代理 `/api` 请求到后端 `http://localhost:8000` (通过 `vite.config.js` 配置)。

#### 2.3.3 数据库 (MySQL)

*   可以使用本地安装的 MySQL，或者通过 Docker 运行一个 MySQL 实例。
*   `docker-compose.yml` 中已包含一个 `db` 服务，可以直接用于开发：
    ```bash
    docker-compose up -d db
    ```
    这会在主机的 `3307` 端口启动一个 MySQL 8.0 服务，数据库名为 `redbook_db`，用户 `redbook_user`，密码 `redbook_password`。
    在本地后端 `.env` 文件中，`DATABASE_URL` 应配置为指向此服务，例如：`mysql+pymysql://redbook_user:redbook_password@localhost:3307/redbook_db`。

### 2.4 Docker 构建与运行 (生产/部署)

1.  **配置 `docker-compose.yml`**:
    *   确保 `backend` 服务下的 `environment` 中的 `DATABASE_URL` 指向的是 Docker 网络中的 `db` 服务 (即 `db:3306`)。
    *   确保 `AI_API_KEY` 和 `SECRET_KEY` 已正确配置。
2.  **构建并启动所有服务**:
    在项目根目录运行:
    ```bash
    docker-compose up -d --build
    ```
3.  **访问**:
    *   前端: `http://localhost` (或服务器IP)
    *   后端API: `http://localhost/api/v1/...` (通过Nginx代理)
4.  **查看日志**:
    ```bash
    docker-compose logs -f backend
    docker-compose logs -f frontend
    docker-compose logs -f db
    ```
5.  **停止服务**:
    ```bash
    docker-compose down
    ```
6.  **打包 Docker 镜像 (用于迁移或独立部署)**:
    如果需要将服务作为独立的镜像分发，可以为每个服务单独构建镜像：
    *   **后端镜像**:
        ```bash
        cd backend
        docker build -t your_username/redbook-backend:latest .
        # 推送到 Docker Hub (可选)
        # docker login
        # docker push your_username/redbook-backend:latest
        ```
    *   **前端镜像**:
        ```bash
        cd frontend
        docker build -t your_username/redbook-frontend:latest .
        # 推送到 Docker Hub (可选)
        # docker push your_username/redbook-frontend:latest
        ```
    之后可以在其他机器上通过 `docker run` 或新的 `docker-compose.yml` 文件来运行这些预构建的镜像。
    **注意**：直接使用 `docker-compose build` 已经完成了镜像的构建，这些镜像存储在本地 Docker 中。如果只是在当前机器运行，无需单独 `docker build`。上述 `docker build` 命令更多用于创建可移植的、带有自定义标签的镜像。

### 2.5 API 接口说明

#### 2.5.1 外部依赖 API

本项目依赖以下外部 API 服务：

1.  **获取用户主页发布 (AIHubMax)**:
    *   URL: `https://aihubmax.com/ability/collect/xhs/user/post`
    *   Method: `POST`
    *   Headers: `Content-Type: application/json`, `Authorization: Bearer <XHS_API_TOKEN>` (此处的Token是您在`docker-compose.yml`中配置的`XHS_API_TOKEN`，如果该服务需要)
    *   Body: `{"cookie": "用户的小红书Cookie", "user_id": "博主的用户ID"}`
    *   用处: 获取指定博主的笔记列表。

2.  **采集笔记内容接口 (AIHubMax)**:
    *   URL: `https://aihubmax.com/ability/collect/xhs/note/detail`
    *   Method: `POST`
    *   Headers: `Content-Type: application/json`, `Authorization: Bearer <XHS_API_TOKEN>`
    *   Body: `{"cookie": "用户的小红书Cookie", "url": "笔记的完整URL，包含xsec_token等参数"}`
    *   用处: 获取单篇笔记的详细内容，包括视频链接、图文信息等。

3.  **Whisper-1 模型 (AIHubMax - 语音转文字)**:
    *   URL: `https://aihubmax.com/v1/audio/transcriptions`
    *   Method: `POST`
    *   Headers: `Authorization: Bearer <AI_API_KEY>`
    *   Body: `multipart/form-data` (包含 `file` 和 `model="whisper-1"`)
    *   用处: 将视频中的音频文件转换为文字。

4.  **Qwen 大语言模型 (AIHubMax - 内容分析)**:
    *   URL: `https://aihubmax.com/v1/chat/completions`
    *   Method: `POST`
    *   Headers: `Accept: application/json`, `Content-Type: application/json`, `Authorization: Bearer <AI_API_KEY>`
    *   Body: `{"model": "qwen3-30b-a3b", "messages": [{"role": "system", ...}, {"role": "user", ...}]}`
    *   用处: 对提取的视频文案进行分析和总结。

#### 2.5.2 项目内部 API (FastAPI)

API 路由定义在 `backend/app/api/v1/endpoints/` 目录下。主要包括：

*   用户认证 (`login.py`)
*   用户管理 (`users.py`)
*   任务管理 (`tasks.py`): 创建任务、获取任务列表、获取任务详情、获取任务下的笔记列表、获取单篇笔记详情等。

详细的API文档可以通过访问运行中后端的 `/docs`路径 (例如 `http://localhost:8000/docs`) 查看 Swagger UI。

### 2.6 后台定时任务

*   项目包含一个后台定时任务 (通过 `apscheduler` 或 FastAPI 的 `BackgroundTasks` / `startup` 事件实现，具体看 `backend/app/main.py` 或相关任务处理模块)。
*   该任务会定期检查数据库中处于特定状态（如 `pending_collection`, `pending_transcript`, `pending_analysis`）的笔记。
*   **执行流程**：
    1.  **笔记采集**：对于 `pending_collection` 状态的笔记，调用外部API获取笔记详情，下载视频（如果适用），更新笔记状态和内容。
    2.  **语音转文字**：对于视频笔记且状态为 `pending_transcript` (或采集完成后自动进入此状态)，提取音频，调用 Whisper API 进行转写，保存文案，更新状态。
    3.  **内容分析**：对于已获取文案（视频笔记）或已采集内容（图文笔记）且状态为 `pending_analysis`，调用 Qwen 模型 API 进行分析，保存结果，更新状态。
*   定时任务的间隔（如每15秒）可以在代码中调整。

### 2.7 代码风格与规范

*   Python: Black, Flake8 (或 Ruff)
*   JavaScript/Vue: Prettier, ESLint
*   请在提交代码前确保通过代码格式化和检查。

### 2.8 未来可优化方向

*   **更精细的错误处理和重试机制**：针对API调用失败、网络波动等情况。
*   **用户体验优化**：如任务编辑功能、更详细的进度展示、批量操作等。
*   **支持更多类型的内容分析**：如图文笔记的图片内容分析。
*   **成本控制提示**：在用户创建任务时，根据规则预估可能的API调用次数和费用。
*   **Cookie管理优化**：提供更便捷的Cookie更新方式，或尝试更稳定的API访问方案。
*   **分页加载**：对于大量笔记的博主，实现分页获取和处理。
*   **更灵活的AI分析Prompt配置**：允许用户自定义分析的侧重点。

---

希望这份文档能帮助您快速上手使用和开发本项目！
```

