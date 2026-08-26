# AI 掘金头条 · 后端（toutiao_backend）

基于 FastAPI 的新闻资讯类后端服务，包含新闻分类/列表/详情、用户注册登录、收藏、浏览历史等接口，并使用 Redis 做读缓存。

## 技术栈

| 类别 | 选型 |
|---|---|
| Web 框架 | FastAPI 0.125 + Starlette + Uvicorn |
| 数据校验 | Pydantic 2.12 |
| ORM | SQLAlchemy 2.0（异步 `AsyncSession`） |
| 数据库 | MySQL（驱动 aiomysql / PyMySQL） |
| 缓存 | Redis（`redis.asyncio`） |
| 密码与鉴权 | passlib + bcrypt，Token 存库校验 |

## 目录结构与分层

```
toutiao_backend/
├── main.py          # 应用入口：注册路由、CORS、全局异常处理器
├── routers/         # 路由层（Controller）
├── crud/            # 数据访问层（DAO / Repository）
├── models/          # 实体层（Entity / PO，SQLAlchemy 表映射）
├── schemas/         # DTO / VO（Pydantic 请求体与响应体）
├── cache/           # Redis 缓存读写
├── config/          # 数据库、Redis 连接与配置
└── utils/           # 通用工具：响应包装、鉴权依赖、异常与异常处理器
```

各目录与经典三层（MVC / 分层架构）的对应关系：

| 目录 | 对应层次 | 判定依据 |
|---|---|---|
| `routers/` | **Controller（路由层）** | `APIRouter` 定义端点，做参数校验与响应组装 |
| `schemas/` | **DTO / VO** | Pydantic 模型，通过 `alias` 完成下划线与驼峰互转 |
| `models/` | **Entity / PO**（不是 DAO） | 仅有 `DeclarativeBase` 表定义、字段、索引，无任何查询代码 |
| `crud/` | **DAO / Repository**（不是 Service） | 内容全是 `select` / `update` 语句，一个函数对应一次数据访问 |
| `cache/` | 缓存访问层（广义 DAO） | 封装 Redis key 规则与读写 |
| `config/` | 配置与连接管理 | 异步引擎、会话工厂、`get_db` 依赖、Redis 客户端 |
| `utils/` | 通用工具 / 横切关注点 | `success_response`、`get_current_user`、统一异常处理 |

> 常见误解：`models` 容易被当成 DAO 层，`crud` 容易被当成 Service 层。实际上 `models` 只是实体定义，`crud` 才是访问数据库的那一层。

## 关于 Service 层

**当前项目没有独立的 Service 层**，业务逻辑被拆散在两个地方：

1. **下沉到了 `routers/`**
   - `routers/news.py` 的列表接口里计算 `offset` 与 `has_more`（分页规则）。
   - 详情接口里编排「查详情 → 浏览量 +1 → 查相关新闻」。
   - `routers/users.py` 的注册接口里编排「用户查重 → 创建用户 → 生成 Token」。

   这些都属于业务编排，标准分层中应位于 Service。

2. **混进了 `crud/`**
   - `crud/news_cache.py` 已不是纯 DAO：它实现了「查缓存 → 未命中查库 → 回写缓存」的缓存旁路（Cache-Aside）策略，还承担了 ORM → Pydantic → dict 的模型转换。
   - 它实质上是一个「带缓存的 Service」，只是被放在了 `crud` 目录下。

### 可选的重构方向

新增 `services/` 目录，把两处逻辑收敛过去，让各层职责回归清晰：

- `routers/` 只负责参数进出与响应包装；
- `services/` 承载业务编排 + 缓存策略 + DTO 转换；
- `crud/` 回归纯粹的 SQL 访问，不感知缓存与 Pydantic。

## 已知问题（待优化）

- **`crud/news.py` 与 `crud/news_cache.py` 大量重复**：`get_news_count`、`increase_news_views` 两份实现完全相同，后续修改容易改漏。
- **同一接口混用两个模块**：`routers/news.py` 的列表接口从 `news_cache` 取列表、却从 `news` 取总数，数据来源不一致。
- **相关新闻返回结构不统一**：`crud/news.py::get_related_news` 手写字典时用了 `publishTime` / `categoryId` 驼峰键，而 `crud/news_cache.py` 版本以 `by_alias=False` 输出下划线键。
- **配置硬编码**：数据库连接串位于 `config/db_conf.py`，Redis 地址位于 `config/cache_conf.py`，建议改为通过环境变量 / `.env`（项目已依赖 `python-dotenv`）注入。
- **CORS 全量放开**：`main.py` 中 `allow_origins=["*"]` 仅适用于开发阶段，生产环境需收窄为具体来源。
- **`echo=True`**：异步引擎开启了 SQL 日志，生产环境建议关闭。

## 本地运行

前置条件：已启动 MySQL（库名 `news_app`）与 Redis（默认 `localhost:6379`）。

```powershell
# 1. 创建并激活虚拟环境
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. 安装依赖
pip install -r requirements.txt

# 3. 按实际环境修改 config/db_conf.py 与 config/cache_conf.py 中的连接配置

# 4. 启动服务
uvicorn main:app --reload
```

启动后可访问：

- 接口文档（Swagger UI）：http://127.0.0.1:8000/docs
- 备用文档（ReDoc）：http://127.0.0.1:8000/redoc

## 接口清单

「鉴权」列标记 ✅ 的接口需通过 `get_current_user` 校验 Token。

### 新闻 `/api/news`

| 方法 | 路径 | 说明 | 鉴权 |
|---|---|---|---|
| GET | `/categories` | 新闻分类列表（走 Redis 缓存） | — |
| GET | `/list` | 按分类分页查询新闻列表 | — |
| GET | `/detail` | 新闻详情，附带浏览量 +1 与相关新闻 | — |

### 用户 `/api/user`

| 方法 | 路径 | 说明 | 鉴权 |
|---|---|---|---|
| POST | `/register` | 注册并返回 Token | — |
| POST | `/login` | 登录并返回 Token | — |
| GET | `/info` | 获取当前用户信息 | ✅ |
| PUT | `/update` | 修改用户信息 | ✅ |
| PUT | `/password` | 修改密码 | ✅ |

### 收藏 `/api/favorite`

| 方法 | 路径 | 说明 | 鉴权 |
|---|---|---|---|
| GET | `/check` | 查询某条新闻是否已收藏 | ✅ |
| POST | `/add` | 添加收藏 | ✅ |
| DELETE | `/remove` | 取消收藏（按 `newsId`） | ✅ |
| GET | `/list` | 分页查询收藏列表 | ✅ |
| DELETE | `/clear` | 清空收藏 | ✅ |

### 浏览历史 `/api/history`

| 方法 | 路径 | 说明 | 鉴权 |
|---|---|---|---|
| POST | `/add` | 新增浏览记录 | ✅ |
| GET | `/list` | 分页查询浏览历史 | ✅ |
| DELETE | `/delete/{history_id}` | 删除单条记录（按记录 ID） | ✅ |
| DELETE | `/clear` | 清空浏览历史 | ✅ |

> 查询参数命名约定：前端传驼峰（`categoryId`、`pageSize`、`newsId`），后端通过 `Query(..., alias=...)` 映射为下划线形式。
