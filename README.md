# NexusOps · 企业级 DevOps 运维平台（领域子系统骨架）

前后端分离的现代化 DevOps 平台脚手架，按 **五大领域子系统** 组织：

| 子系统 | 后端包 | 前端前缀 | 职责 |
| --- | --- | --- | --- |
| 技术底座 | `core` | — | 统一响应信封、全局异常、基础模型、JWT 认证、WS 鉴权中间件（不含任何业务） |
| 监控中心 | `apps.monitor` | `/monitor` | 平台组件健康探针、告警/指标（演进中） |
| 配置中心 | `apps.cmdb` | `/cmdb` | 多环境集群配置、主机资产、配置项（吸收原环境管理） |
| 运维中心 | `apps.ops` | `/ops` | Web 终端、批量作业、变更管控（承接原 WebSocket 占位） |
| 持续交付 | `apps.cicd` | `/cicd` | 流水线、构建、发布（Pipeline 模型占位） |

技术栈：**Django 5 + DRF + SimpleJWT + Channels 4(Daphne) + Celery + Redis + PostgreSQL** / **Vue 3 + Vite + Tailwind CSS + Element Plus + Pinia + Axios**。

## 后端分层

每个领域应用严格按 `models / serializers / services / views` 分层，业务逻辑唯一归属 `services/`（事务编排、状态机、外部交互），View 仅做分发与信封包装，Model 仅有字段与纯数据行为。

```
backend/
├── config/                     # 项目配置层（无 Admin）
│   ├── settings.py             #   JWT/Channels/Celery；注册 core + 四个领域应用
│   ├── urls.py                 #   REST 按 /api/v1/<domain>/ 解耦挂载（无 admin）
│   ├── asgi.py                 #   ASGI：聚合各领域 ws_urls，http/ws 协议解耦
│   ├── wsgi.py                 #   WSGI（gunicorn）：纯 REST
│   ├── celery_app.py           #   Celery 实例 + beat 调度
│   └── auth_urls 由 core 提供   #   /api/v1/auth/token[/refresh]
├── core/                       # 技术底座（零业务）
│   ├── responses.py            #   统一信封 {code,message,data}
│   ├── exceptions.py           #   业务异常 + DRF 全局异常处理
│   ├── middleware.py           #   全局未捕获异常兜底
│   ├── pagination.py / models.py  # 分页结构 / TimeStamped·SoftDelete 基类
│   ├── auth_urls.py            #   JWT token 路由
│   └── ws.py                   #   WebSocket JWT 鉴权中间件（横切能力）
└── apps/
    ├── monitor/                # 监控中心
    │   ├── services/health_service.py   # DB/Redis/Celery 探活
    │   ├── views/health_views.py        # 三级探针
    │   └── urls.py             #   /api/v1/monitor/healthz[/ready|/live]
    ├── cmdb/                   # 配置中心（原 environments 升级并入）
    │   ├── models|serializers|services|views/environment*
    │   └── urls.py             #   /api/v1/cmdb/environments
    ├── ops/                    # 运维中心
    │   ├── consumers.py        #   TerminalConsumer（原 core Echo 占位升级）
    │   ├── ws_urls.py          #   /ws/ops/terminal/<host_id>/
    │   ├── services/host_service.py
    │   ├── views/terminal_views.py
    │   └── urls.py             #   /api/v1/ops/hosts
    └── cicd/                   # 持续交付
        ├── models/pipeline.py          # Pipeline 基础模型
        ├── serializers|services|views/pipeline*
        ├── tasks.py                    # run_pipeline 异步任务占位
        └── urls.py             #   /api/v1/cicd/pipelines
```

### 关键约定

- **无 Admin**：`INSTALLED_APPS` 不含 `django.contrib.admin`、`django.contrib.messages`；根路由零 `admin.site.urls`。
- **JWT**：`JWTAuthentication` 为 DRF 默认认证；Access 30min / Refresh 7d（HS256，密钥走环境变量）。
  - `POST /api/v1/auth/token/`、`POST /api/v1/auth/token/refresh/`
- **统一信封** `{"code":0,"message":"success","data":...}`，DRF exception handler + `GlobalExceptionMiddleware` 双兜底。
- **双协议栈**：`web`(gunicorn/WSGI:8000) 承载 REST；`daphne`(ASGI:8001) 承载 HTTP + WebSocket；各领域在自己的 `ws_urls.py` 声明实时通道，`config/asgi.py` 统一聚合。
- **健康探针（monitor 提供，三级）**：
  - `GET /api/v1/monitor/healthz/live`：存活（进程可响应）；
  - `GET /api/v1/monitor/healthz/ready`：就绪（DB+Redis），容器 healthcheck 使用，避免与 worker 循环依赖；
  - `GET /api/v1/monitor/healthz`：完整（DB+Redis+Celery ping），供运维观测，异常返回 503。

## 前端

```
frontend/src/
├── layouts/        # MainLayout + SideNav(5 大系统) + TopBar + EnvSwitcher
├── components/domain/  # DomainHome / MetricCard / EntryCard 子系统首页骨架
├── api/            # http（信封解包/JWT 注入/静默续期）+ auth/cmdb/ops/cicd
├── stores/         # Pinia: auth / app
└── views/
    ├── monitor/    # MonitorHomeView（指标+告警流+构建面板）
    ├── cmdb/       # CmdbHomeView + environments/（环境管理）
    ├── ops/        # OpsHomeView + terminal/（Web 终端占位）
    ├── cicd/       # CicdHomeView + pipelines/（流水线看板）
    ├── settings/   # SettingsHomeView
    └── login/
```

- 深色科技风：Slate/Zinc 灰黑基底 + Indigo/Cyan 强调，样式全部 Tailwind Utility Classes。
- 布局：左侧可折叠五大系统导航 + 顶部面包屑/Dev·Staging·Prod 环境切换器 + 主工作区。
- 每个子系统首页基于 `DomainHome` 统一骨架：核心指标卡片 + 功能入口；复杂功能页拆分子组件，**单文件最大 118 行（约束 300）**。
- 旧路径（`/dashboard`、`/pipelines`、`/terminal`、`/settings/environments`）已配置重定向到新路由。

## docker-compose 服务

| 服务 | 端口 | 说明 |
| --- | --- | --- |
| **frontend** | **80** (`FRONTEND_PORT`) | **平台唯一对外入口**：Nginx 托管 SPA，反代 `/api`→web、`/ws`→daphne |
| web | 8000 (`WEB_PORT`) | gunicorn/WSGI，纯 REST（调试用，也可不暴露） |
| daphne | 8001 (`ASGI_PORT`) | ASGI，HTTP + WebSocket（调试用） |
| celery-worker / celery-beat | — | 任务执行与定时调度 |
| postgres / redis | 5432 / 6379 | 数据库与缓存/队列 |

Nginx 关键点：`try_files ... /index.html` 保证 SPA 深层路由刷新不 404；`/api/` 反代 gunicorn、`/ws/` 携带 `Upgrade` 头反代 Daphne；upstream 用 Docker 内置 DNS 变量动态解析，后端重启时 Nginx 不崩溃。消费方等待 `web` 通过就绪探针后再启动；Redis db0=broker / db1=result / db2=channel layer。

## 一键启动

```bash
cp .env.example .env
cp backend/.env.example backend/.env      # 按实际修改密钥与连接串
docker compose up -d --build
```

浏览器直接打开 **http://localhost** 即为完整平台（前端静态资源 + 接口 + WebSocket 全部经 Nginx :80 同源转发，无需本地跑前端、无跨域）。

仅做前端本地开发时：`cd frontend && npm install && npm run dev`，Vite 已配置 `/api`→`:8000`、`/ws`→`:8001` 代理（此时需本地或 compose 起后端）。

## 验证

```bash
# 健康探针（经 Nginx :80）
curl http://localhost/api/v1/monitor/healthz          # DB + Redis + Celery
curl http://localhost/api/v1/monitor/healthz/ready    # DB + Redis（容器探针）

# 全链路 Request-ID：响应头与信封体均带回同一 ID
curl -i http://localhost/api/v1/monitor/healthz/live
#   HTTP/1.1 200 ...  X-Request-ID: 9f1c... 
#   {"code":0,...,"request_id":"9f1c..."}

# 登录（信封同样含 request_id）
curl -X POST http://localhost/api/v1/auth/token/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"ChangeMe123!"}'

# WebSocket 终端（需 JWT），request_id 可经查询串透传
# ws://localhost/ws/ops/terminal/prod-web-01/?token=<access_token>&request_id=<rid>
```

## 全链路 Request-ID（TraceID）

一套贯穿前端 → Nginx → Django/Celery/Channels 的请求追踪：

- **前端**：Axios 请求拦截器为每个请求生成唯一 ID 并携带 `X-Request-ID`（`crypto.randomUUID`）；响应错误时弹窗与控制台均显示该 ID（短 8 位便于报障，控制台留全量）。WebSocket 建连经 `?request_id=` 透传。
- **后端入口**：`core.middleware.RequestIdMiddleware` 置于中间件最外层——入站优先复用客户端 ID（白名单校验防日志注入），缺失则生成，写入 `contextvar` 并在**响应头** `X-Request-ID` 与**统一信封体** `request_id` 字段双双回传；DRF 异常处理器、JWT 登录接口、全局 500 兜底均带 ID。
- **日志**：`core.logging_utils.RequestIDFilter` 挂载到 Console 与 RotatingFile Handler，**每条控制台/文件日志前自动打印 `[rid:xxxxxxxx]`**；文件输出到容器 `/app/logs/app.log`（compose 中以 `app_logs` 卷持久化，`docker compose exec web sh -c 'grep <rid> /app/logs/app.log'` 即可串联整条链路）。
- **异步与长连**：Celery 通过 `before_task_publish/task_prerun` 信号把 HTTP 请求的 ID 透传进任务（beat 自发任务则新生成）；Channels 中间件为每个 WS 连接设置 ID，终端通道消息也带回。

排障路径：用户报错弹窗上的 8 位 ID → 后端日志 `grep <rid>` → 同时可在浏览器 Network 响应头/信封体核对。

## 后续扩展

- ops 终端接入 xterm.js + 真实 SSH（asyncssh），审计落库；后端 `TerminalConsumer` 已就位。
- cicd 扩展 PipelineRun / Stage 模型与 Celery 编排状态机。
- cmdb 增加主机/拓扑模型，ops 主机清单改由 cmdb 聚合。
- 接入 OpenAPI（drf-spectacular）、结构化日志与 Prometheus 指标。
