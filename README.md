# AI 掘金头条 · 后端（toutiao_backend）

基于 FastAPI 的新闻资讯类后端服务，包含新闻分类/列表/详情、用户注册登录、收藏、浏览历史等接口，并使用 Redis 做读缓存。

> 📚 **学习文档在 [`docs/`](./docs/) 目录**：
> [项目学习笔记（从这里开始）](./docs/项目学习笔记.md) — 项目里用到的 FastAPI + SQLAlchemy + Pydantic，锚定到文件行号
> · [FastAPI 完全手册](./docs/FastAPI完全手册.md)
> · [SQLAlchemy 2.0 完全手册](./docs/SQLAlchemy2完全手册.md)
> · [Pydantic v2 完全手册](./docs/Pydantic2完全手册.md)
> — 后三份各自覆盖对应框架的**全部**知识，不受本项目规模限制。
>
> 本文只管**接口清单与运行说明**；想学知识点看 `docs/`。

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
├── utils/           # 通用工具：响应包装、鉴权依赖、异常与异常处理器
└── docs/            # 学习文档：项目学习笔记 + FastAPI/SQLAlchemy/Pydantic 三份完全手册
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

> 每条均已对照当前代码核实。更详尽的分析与修法见
> [`docs/项目学习笔记.md` §7【代码里埋的坑】](./docs/项目学习笔记.md#7-代码里埋的坑已核实)。

- 🔴 **删除浏览历史的字段错配**：`routers/history.py:58` 把路径上的 `history_id` 传给了
  `crud/history.py:49` 的 `news_id` 参数，最终 SQL 条件是 `History.news_id == history_id`。
  它删的不是「指定记录」而是「该用户下 news_id 恰好等于这个数字的记录」。
  修法：把 `crud` 里的条件改为 `History.id == history_id` 并重命名参数。
- 🔴 **`models/users.py:33,34,58` 的 `default=datetime.now()` 多了一对括号**：
  默认值在模块导入时就被求值一次，所有用户的 `created_at` 都是服务启动时间。
  应该传函数本体（`default=datetime.now`）。`models/news.py` 里的写法是对的，可对照。
- 🟡 **四个 `Base` 各自为政**：`models/` 下四个文件各自定义了 `class Base(DeclarativeBase)`，
  导致四份互相隔离的 `metadata`。`create_all()` 一次只能建出其中一部分表，Alembic 的
  `--autogenerate` 也无法工作。应抽出单一的 `models/base.py`。
- 🟡 **浏览量与详情缓存不一致**：`crud/news.py::increase_news_views` 只写库，不失效
  `news:detail:{id}`。详情缓存 TTL 300s 内，前端看到的浏览量是陈的。
- 🟡 **列表接口的 COUNT 没过缓存**：`routers/news.py:38-39` 两次调用都走 `news_cache`，
  但 `crud/news_cache.py::get_news_count` 本体直接查库、没有缓存。
  结果是即使列表命中缓存，每次请求仍然会打一条 `COUNT(*)`，缓存收益被削掉一半。
- 🟡 **连接池缺 `pool_recycle` / `pool_pre_ping`**：`config/db_conf.py:7-12` 只设了
  `pool_size` 与 `max_overflow`。MySQL 会切掉空闲连接，而连接池里仍留着这个死连接，
  长时间空闲后的第一个请求很可能报 `MySQL server has gone away`。
- 🟡 **漏注册 `RequestValidationError`**：`utils/exception_handlers.py` 注册了四个处理器但不包括它，
  所以参数校验失败时返回的是 FastAPI 默认的 422 结构，与其他接口的统一包装不一致。
- 🟡 **CORS 配置违反规范**：`main.py:23-24` 同时设了 `allow_origins=["*"]` 与
  `allow_credentials=True`，浏览器会直接拒绝这种组合。生产环境需收窄为具体来源。
- 🟡 **DAO 层抛 HTTP 异常**：`crud/users.py:108` 在数据访问层直接 `raise HTTPException`，
  让 `crud` 耦合了 Web 层概念，与其他函数「返回 None / bool 交给路由判断」的风格不统一。
- 🟡 **`crud/users.py:46-52` 的 commit 不对称**：`create_token` 新建分支 commit 了，
  更新分支没 commit，靠 `get_db` 兜底。这也暗示了更大的问题：`crud` 与 `get_db` 双重 commit，
  使得「创建用户 + 生成 Token」无法作为一个事务回滚。
- 🟢 **时区基准三套混用**：`datetime.now()`、`datetime.utcnow`、`datetime.now(timezone.utc)`
  在不同文件里共存，跳过 8 小时时差。建议全项目统一用 UTC 入库，展示层再转。
- 🟢 **配置与密钥硬编码**：数据库连接串位于 `config/db_conf.py`，Redis 地址位于
  `config/cache_conf.py`，`SECRET_KEY` 位于 `utils/jwt_util.py`。建议改用 `pydantic-settings`
  从环境变量 / `.env` 注入（项目已依赖 `python-dotenv`）。
- 🟢 **`echo=True`**：异步引擎开启了 SQL 日志，学习期有用，生产环境建议关闭。
- 🟢 **残留代码**：`requirements.txt` 同时列了已废弃的 `aioredis` 与实际在用的 `redis`；
  `test_main.http` 里的 `/hello/User` 路由已不存在；`routers/users.py:40-83` 是教学用伪代码注释块。

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
| DELETE | `/delete/{history_id}` | 删除单条记录。⚠️ **当前实现有 bug**：路径参数被当成 `news_id` 用，实际删的是该用户下 `news_id` 等于此值的记录 | ✅ |
| DELETE | `/clear` | 清空浏览历史 | ✅ |

> 查询参数命名约定：前端传驼峰（`categoryId`、`pageSize`、`newsId`），后端通过 `Query(..., alias=...)` 映射为下划线形式。
