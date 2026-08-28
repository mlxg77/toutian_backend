# SQLAlchemy 2.0 完全学习手册

> 本手册基于 SQLAlchemy 2.0 官方文档整理，结合「掘金头条」后端项目（toutiao_backend）的实际代码作为案例。
> 适合零基础小白从头学起，重点聚焦 **ORM 异步模式**，这也是 FastAPI 项目中最常用的方式。

---

## 目录

- [第一章 SQLAlchemy 简介与安装](#第一章-sqlalchemy-简介与安装)
- [第二章 核心概念总览](#第二章-核心概念总览)
- [第三章 数据库引擎（Engine）](#第三章-数据库引擎engine)
- [第四章 会话（Session）](#第四章-会话session)
- [第五章 声明式模型（Declarative Models）](#第五章-声明式模型declarative-models)
- [第六章 列类型与列选项](#第六章-列类型与列选项)
- [第七章 表约束与索引](#第七章-表约束与索引)
- [第八章 CRUD 操作——创建（Create）](#第八章-crud-操作创建create)
- [第九章 CRUD 操作——查询（Read）](#第九章-crud-操作查询read)
- [第十章 CRUD 操作——更新（Update）](#第十章-crud-操作更新update)
- [第十一章 CRUD 操作——删除（Delete）](#第十一章-crud-操作删除delete)
- [第十二章 关系与外键（Relationships & Foreign Keys）](#第十二章-关系与外键relationships--foreign-keys)
- [第十三章 联表查询（JOIN）](#第十三章-联表查询join)
- [第十四章 异步支持（Asyncio）](#第十四章-异步支持asyncio)
- [第十五章 事务管理与 Session 生命周期](#第十五章-事务管理与-session-生命周期)
- [第十六章 ORM 对象的状态流转](#第十六章-orm-对象的状态流转)
- [第十七章 聚合函数与分组](#第十七章-聚合函数与分组)
- [第十八章 项目实战总结](#第十八章-项目实战总结)

---

## 第一章 SQLAlchemy 简介与安装

### 1.1 什么是 SQLAlchemy？

SQLAlchemy 是 Python 最流行的 **ORM（Object-Relational Mapping，对象关系映射）** 框架。它让你用 Python 类和对象来操作数据库，而不是写原始 SQL。

**核心思想：**
```
Python 类  →  数据库表
Python 对象 →  数据库行
对象属性    →  列值
```

### 1.2 SQLAlchemy 的两层架构

```
┌──────────────────────────────────┐
│         ORM 层（高层）            │
│   声明式模型、Session、查询构造    │
├──────────────────────────────────┤
│        Core 层（底层）            │
│   Engine、SQL 表达式、Connection  │
├──────────────────────────────────┤
│        DBAPI 驱动层              │
│   aiomysql / pymysql / psycopg2  │
└──────────────────────────────────┘
```

- **Core 层**：提供 SQL 表达式语言，接近原始 SQL，但用 Python 语法编写
- **ORM 层**：在 Core 之上，提供对象映射，操作 Python 对象就等于操作数据库

### 1.3 安装

```bash
# 基础安装
pip install sqlalchemy

# 配合 MySQL 异步驱动
pip install sqlalchemy aiomysql

# 配合 MySQL 同步驱动
pip install sqlalchemy pymysql
```

> 💡 **掘金头条项目** 使用 SQLAlchemy 2.0.45 + aiomysql 0.3.2，全异步模式。

### 1.4 SQLAlchemy 2.0 vs 1.x 的关键变化

| 特性 | 1.x 风格 | 2.0 风格（推荐） |
|------|----------|----------------|
| 模型定义 | `Column(Integer)` | `mapped_column(Integer)` |
| 类型注解 | 不需要 | 使用 `Mapped[type]` |
| 查询方式 | `session.query(User)` | `session.execute(select(User))` |
| 异步支持 | 需要第三方库 | 原生支持 |

---

## 第二章 核心概念总览

在开始写代码之前，先理解这些核心概念：

| 概念 | 说明 | 类比 |
|------|------|------|
| **Engine** | 数据库连接的管理器，负责连接池和 SQL 执行 | 相当于数据库的"大门" |
| **Session** | 与数据库的一次"对话"，管理事务和对象 | 相当于和数据库的"聊天窗口" |
| **Model（模型类）** | Python 类，对应数据库中的一张表 | 相当于表的"设计图" |
| **Instance（实例）** | 模型类的对象，对应数据库中的一行 | 相当于表里的一条记录 |
| **Statement（语句）** | SQL 操作（select、insert、update、delete） | 相当于 SQL 语句 |
| **Result（结果集）** | 查询返回的结果 | 相当于查询结果的"表格" |

**典型工作流程：**
```
1. 创建 Engine → 连接数据库
2. 定义 Model → 创建表结构
3. 创建 Session → 开始一个"对话"
4. 执行 CRUD → 增删改查
5. Commit / Rollback → 提交或回滚事务
6. 关闭 Session → 结束"对话"
```

---

## 第三章 数据库引擎（Engine）

### 3.1 什么是 Engine？

Engine 是 SQLAlchemy 的**起点**，它负责：
- 管理**连接池**（Connection Pool）——复用数据库连接，避免频繁创建/销毁
- 执行 **SQL 语句**
- 与 **DBAPI 驱动**交互（如 aiomysql、pymysql）

### 3.2 创建同步 Engine

```python
from sqlalchemy import create_engine

# 数据库 URL 格式：dialect+driver://user:password@host:port/database
engine = create_engine(
    "mysql+pymysql://root:123456@localhost:3306/news_app?charset=utf8mb4",
    echo=True,           # 打印 SQL 语句（调试用）
    pool_size=5,         # 连接池中保持的连接数
    max_overflow=10      # 连接池满时允许创建的额外连接数
)
```

### 3.3 创建异步 Engine（FastAPI 项目推荐）

```python
from sqlalchemy.ext.asyncio import create_async_engine

# 注意：dialect 变成了 mysql+aiomysql
async_engine = create_async_engine(
    "mysql+aiomysql://root:123456@localhost:3306/news_app?charset=utf8mb4",
    echo=True,
    pool_size=10,        # 连接池大小
    max_overflow=20      # 溢出连接数
)
```

### 3.4 数据库 URL 格式详解

```
dialect+driver://username:password@host:port/database?params
│       │          │        │        │     │    │      │
│       │          │        │        │     │    │      └─ 额外参数
│       │          │        │        │     │    └─ 数据库名
│       │          │        │        │     └─ 端口号
│       │          │        │        └─ 主机地址
│       │          │        └─ 密码
│       │          └─ 用户名
│       └─ 数据库驱动
└─ 数据库类型（mysql, postgresql, sqlite 等）
```

常见 URL 示例：
```python
# MySQL 同步
"mysql+pymysql://root:password@localhost:3306/mydb"

# MySQL 异步
"mysql+aiomysql://root:password@localhost:3306/mydb"

# SQLite（文件）
"sqlite:///./database.db"

# SQLite（内存）
"sqlite:///:memory:"

# PostgreSQL 异步
"postgresql+asyncpg://user:password@localhost:5432/mydb"
```

### 3.5 连接池参数详解

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `pool_size` | 5 | 连接池中保持的持久连接数 |
| `max_overflow` | 10 | 连接池满时允许创建的额外连接数 |
| `pool_timeout` | 30 | 获取连接的最大等待时间（秒） |
| `pool_recycle` | -1 | 连接回收时间（秒），MySQL 建议设为 3600 |
| `echo` | False | 是否打印 SQL 语句 |

> 💡 **掘金头条项目案例**——数据库引擎配置：
> ```python
> # config/db_conf.py
> from sqlalchemy.ext.asyncio import create_async_engine
>
> ASYNC_DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/news_app?charset=utf8mb4"
>
> async_engine = create_async_engine(
>     ASYNC_DATABASE_URL,
>     echo=True,
>     pool_size=10,
>     max_overflow=20
> )
> ```

---

## 第四章 会话（Session）

### 4.1 什么是 Session？

Session 是 SQLAlchemy 中最重要的概念之一。你可以把它理解为：

> **Session 就是你和数据库之间的"对话窗口"。在这个窗口里，你可以查询、新增、修改、删除数据，最后统一提交（commit）或撤销（rollback）。**

### 4.2 创建同步 Session

```python
from sqlalchemy.orm import sessionmaker, Session

# 创建 Session 工厂
SessionLocal = sessionmaker(bind=engine, class_=Session)

# 使用 Session
with SessionLocal() as session:
    # 执行数据库操作...
    session.commit()
```

### 4.3 创建异步 Session（推荐）

```python
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

# 创建异步 Session 工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False   # 提交后不自动过期对象属性（重要！）
)
```

### 4.4 在 FastAPI 中使用 Session（依赖注入）

```python
# config/db_conf.py
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session            # 把 session 交给路由使用
            await session.commit()   # 路由正常执行后，提交事务
        except Exception:
            await session.rollback() # 出错时回滚
            raise
        finally:
            await session.close()    # 关闭连接
```

**执行流程：**
```
1. async with AsyncSessionLocal() as session → 创建 session
2. yield session → 把 session 交给路由函数使用
3. 路由函数执行完毕 → 继续往下执行
4. await session.commit() → 提交所有更改到数据库
5. 如果出错 → await session.rollback() → 撤销所有更改
6. finally → await session.close() → 无论如何都关闭连接
```

> 💡 **掘金头条项目案例**——完整的 Session 工厂配置：
> ```python
> # config/db_conf.py
> AsyncSessionLocal = async_sessionmaker(
>     bind=async_engine,
>     class_=AsyncSession,
>     expire_on_commit=False  # 提交后仍可使用对象属性，不会再偷偷查数据库
> )
> ```
> `expire_on_commit=False` 非常关键！如果设为 True（默认值），`commit()` 之后对象的所有属性都会变成"过期"状态，再访问属性会自动触发一条新的 SELECT 查询。在 FastAPI 中通常设为 False。

---

## 第五章 声明式模型（Declarative Models）

### 5.1 什么是声明式模型？

声明式模型就是用 Python 类来**描述数据库表的结构**。SQLAlchemy 会根据你的类定义自动创建对应的数据库表。

### 5.2 定义 Base 基类

所有模型类都必须继承一个 **DeclarativeBase**：

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

### 5.3 定义模型类（SQLAlchemy 2.0 风格）

```python
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"   # 指定数据库表名

    # Mapped[type] 是 2.0 的类型注解方式
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
```

### 5.4 关键语法解析

#### Mapped[type] 类型注解

`Mapped[type]` 是 SQLAlchemy 2.0 的类型注解方式，告诉 SQLAlchemy 这个列的 Python 类型：

```python
# 必填列（NOT NULL）
id: Mapped[int]                    # 整数，不能为 None
name: Mapped[str]                  # 字符串，不能为 None

# 可选列（允许 NULL）
nickname: Mapped[Optional[str]]    # 字符串，可以为 None
bio: Mapped[str | None]            # 同上（Python 3.10+ 语法）
```

#### mapped_column() 定义列

`mapped_column()` 定义数据库列的详细信息：

```python
mapped_column(
    类型,                      # SQLAlchemy 列类型（Integer, String 等）
    primary_key=True,          # 是否为主键
    autoincrement=True,        # 是否自增
    nullable=False,            # 是否允许 NULL
    unique=True,               # 是否唯一
    default=值或函数,           # 默认值
    onupdate=值或函数,          # 更新时的值
    comment="注释",            # 列注释（MySQL）
    index=True                 # 是否创建索引
)
```

### 5.5 带公共字段的 Base 基类

如果多张表都有 `created_at` 和 `updated_at` 字段，可以把它们放在 Base 中：

```python
from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    # 在 Base 中定义的字段，所有继承它的模型类都会自动拥有
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )
```

> 💡 **掘金头条项目案例**——`models/news.py` 就是这样做的：
> ```python
> class Base(DeclarativeBase):
>     created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
>     updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
>
> class Category(Base):
>     __tablename__ = "news_category"
>     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
>     name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
>     sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
> ```

### 5.6 __tablename__ 表名

每个模型类必须指定 `__tablename__`，否则 SQLAlchemy 会使用类名的小写形式作为表名。

```python
class User(Base):
    __tablename__ = "user"        # 表名是 user
    ...

class Category(Base):
    __tablename__ = "news_category"  # 表名是 news_category
    ...
```

### 5.7 创建数据库表

```python
# 同步方式
Base.metadata.create_all(engine)

# 异步方式
async with async_engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
```

⚠️ **注意**：`create_all()` 只会创建**该 Base 的 metadata 中注册的表**。如果项目中有多个不同的 `Base` 类，需要分别调用。

> 💡 **掘金头条项目的坑**：项目中 `models/news.py`、`models/users.py`、`models/favorite.py` 各自定义了独立的 `Base` 类，导致有 4 个不同的 `metadata` 对象，`create_all()` 无法一次性创建所有表。最佳实践是全项目共用一个 `Base`。

---

## 第六章 列类型与列选项

### 6.1 常用列类型

```python
from sqlalchemy import (
    Integer,      # 整数 → INT
    String,       # 字符串 → VARCHAR(n)
    Text,         # 长文本 → TEXT
    Float,        # 浮点数 → FLOAT
    Boolean,      # 布尔值 → BOOLEAN / TINYINT
    DateTime,     # 日期时间 → DATETIME
    Date,         # 日期 → DATE
    Time,         # 时间 → TIME
    Enum,         # 枚举 → ENUM
    JSON,         # JSON 数据 → JSON
    BigInteger,   # 大整数 → BIGINT
    Numeric,      # 精确小数 → DECIMAL
)
```

### 6.2 类型使用示例

```python
from typing import Optional
from datetime import datetime
from sqlalchemy import Integer, String, Text, Float, Boolean, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

class Product(Base):
    __tablename__ = "product"

    # 整数
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # 字符串（指定长度）
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # 长文本
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # 浮点数
    price: Mapped[float] = mapped_column(Float, nullable=False)
    
    # 布尔值
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # 日期时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # 枚举
    status: Mapped[str] = mapped_column(
        Enum('draft', 'published', 'archived'),
        default='draft'
    )
```

### 6.3 常用列选项

| 选项 | 说明 | 示例 |
|------|------|------|
| `primary_key=True` | 主键 | `mapped_column(Integer, primary_key=True)` |
| `autoincrement=True` | 自增 | `mapped_column(Integer, autoincrement=True)` |
| `nullable=False` | 不允许 NULL | `mapped_column(String(50), nullable=False)` |
| `unique=True` | 唯一约束 | `mapped_column(String(50), unique=True)` |
| `default=值` | 默认值 | `mapped_column(Integer, default=0)` |
| `default=函数` | 动态默认值 | `mapped_column(DateTime, default=datetime.now)` |
| `onupdate=函数` | 更新时的值 | `mapped_column(DateTime, onupdate=datetime.now)` |
| `comment="..."` | 列注释 | `mapped_column(String(50), comment="用户名")` |
| `index=True` | 创建索引 | `mapped_column(String(50), index=True)` |

> 💡 **掘金头条项目案例**——性别枚举列：
> ```python
> # models/users.py
> gender: Mapped[Optional[str]] = mapped_column(
>     Enum('male', 'female', 'unknown'),
>     comment="性别",
>     default='unknown'
> )
> ```

---

## 第七章 表约束与索引

### 7.1 使用 __table_args__ 定义表级别约束

```python
from sqlalchemy import UniqueConstraint, Index, ForeignKey

class Favorite(Base):
    __tablename__ = "favorite"

    # 表级别约束和索引
    __table_args__ = (
        # 唯一约束：同一用户只能收藏同一新闻一次
        UniqueConstraint('user_id', 'news_id', name='user_news_unique'),
        
        # 索引：加速按 user_id 查询
        Index('fk_favorite_user_idx', 'user_id'),
        
        # 索引：加速按 news_id 查询
        Index('fk_favorite_news_idx', 'news_id'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    news_id: Mapped[int] = mapped_column(Integer, ForeignKey("news.id"), nullable=False)
```

### 7.2 常见约束类型

| 约束 | 说明 | 语法 |
|------|------|------|
| **PRIMARY KEY** | 主键 | `primary_key=True`（列级别） |
| **UNIQUE** | 唯一 | `unique=True`（列级别）或 `UniqueConstraint`（表级别） |
| **FOREIGN KEY** | 外键 | `ForeignKey("表名.列名")` |
| **INDEX** | 索引 | `Index('索引名', '列名')` |
| **CHECK** | 检查约束 | `CheckConstraint('条件')` |

### 7.3 索引的作用

索引就像书的**目录**，能大幅提升查询速度：

```python
class News(Base):
    __tablename__ = "news"
    __table_args__ = (
        # 高频查询场景：按 category_id 查新闻列表
        Index('fk_news_category_idx', 'category_id'),
        # 按发布时间排序
        Index('idx_publish_time', 'publish_time'),
    )
```

**什么时候该建索引？**
- WHERE 条件中频繁使用的列
- ORDER BY 排序的列
- JOIN 连接的列

**什么时候不该建？**
- 表很小的时候（索引反而增加开销）
- 频繁 UPDATE/INSERT 的列（每次修改都要更新索引）

---

## 第八章 CRUD 操作——创建（Create）

### 8.1 新增单条记录

```python
# 1. 创建 ORM 对象（此时 id 为 None，数据只在内存中）
user = User(username="zhangsan", password="hashed_password")

# 2. 添加到 Session（此时数据进入"待插入"状态）
session.add(user)

# 3. 提交事务（此时才真正执行 INSERT INTO）
await session.commit()

# 4. 刷新对象（从数据库读回最新数据，包括自动生成的 id）
await session.refresh(user)

# 现在 user.id 就有值了
print(user.id)  # → 1
```

**执行过程：**
```
内存对象 → add() → 待插入 → commit()/flush() → INSERT INTO → 数据库
                                                           ↓
                                              refresh() ← 读回 id
```

### 8.2 为什么需要 refresh？

```python
user = User(username="zhangsan", password="xxx")
# 此时 user.id 是 None
session.add(user)
await session.commit()
# commit 之后，数据库已经给 user 分配了 id
# 但 Python 对象还不知道自己的 id 是什么！
await session.refresh(user)
# refresh 从数据库读回最新数据，user.id 现在正确了
```

### 8.3 封装为 CRUD 函数

> 💡 **掘金头条项目案例**——创建用户：
> ```python
> # crud/users.py
> async def create_user(db: AsyncSession, user_data: UserRequest):
>     hashed_password = security.get_hash_password(user_data.password)
>     user = User(username=user_data.username, password=hashed_password)
>     db.add(user)
>     await db.commit()
>     await db.refresh(user)   # 从数据库读回 id
>     return user
> ```

> 💡 **掘金头条项目案例**——添加收藏：
> ```python
> # crud/favorite.py
> async def add_news_favorite(db: AsyncSession, user_id: int, news_id: int):
>     favorite = Favorite(user_id=user_id, news_id=news_id)
>     db.add(favorite)
>     await db.commit()
>     await db.refresh(favorite)
>     return favorite
> ```

### 8.4 批量插入

```python
# 方式一：逐个 add
for item in items:
    session.add(item)
await session.commit()

# 方式二：使用 add_all（更高效）
session.add_all([
    User(username="user1", password="xxx"),
    User(username="user2", password="yyy"),
    User(username="user3", password="zzz"),
])
await session.commit()

# 方式三：使用 Core 的 insert()（批量插入最高效）
from sqlalchemy import insert
stmt = insert(User).values([
    {"username": "user1", "password": "xxx"},
    {"username": "user2", "password": "yyy"},
])
await session.execute(stmt)
await session.commit()
```

---

## 第九章 CRUD 操作——查询（Read）

### 9.1 基本查询语法

SQLAlchemy 2.0 使用 `select()` 构造查询语句：

```python
from sqlalchemy import select

# 查询所有用户
stmt = select(User)
result = await session.execute(stmt)
users = result.scalars().all()   # 获取所有 ORM 对象
```

### 9.2 结果集（Result）的常用方法

```python
result = await session.execute(stmt)

# 获取方式一：scalars() → 返回 ORM 对象
result.scalars().all()          # 所有结果（列表）
result.scalars().first()        # 第一个结果（没有返回 None）
result.scalar_one()             # 必须且只能有一个结果（否则报错）
result.scalar_one_or_none()     # 最多一个结果（没有返回 None）

# 获取方式二：直接获取元组
result.all()                    # 所有结果（元组列表）
result.first()                  # 第一个结果
result.one()                    # 必须且只能有一个
result.one_or_none()            # 最多一个
```

**选择指南：**

| 方法 | 用途 | 找不到 | 多条 |
|------|------|--------|------|
| `scalar_one()` | 确定只有一条 | 报错 | 报错 |
| `scalar_one_or_none()` | 最多一条 | 返回 None | 报错 |
| `scalars().all()` | 可能多条 | 返回空列表 | 返回全部 |
| `scalars().first()` | 只需要第一条 | 返回 None | 只取第一条 |

### 9.3 WHERE 条件查询

```python
from sqlalchemy import select

# 方式一：.where() 链式调用
stmt = select(User).where(User.username == "zhangsan")

# 方式二：.filter_by() 简化写法（等值条件）
stmt = select(User).filter_by(username="zhangsan")

# 多个条件（默认 AND）
stmt = select(User).where(
    User.username == "zhangsan",     # 条件1
    User.is_active == True            # 条件2
)

# OR 条件
from sqlalchemy import or_
stmt = select(User).where(
    or_(User.username == "zhangsan", User.username == "lisi")
)
```

### 9.4 常用查询运算符

```python
# 比较
User.age == 18             # 等于
User.age != 18             # 不等于
User.age > 18              # 大于
User.age >= 18             # 大于等于
User.age < 18              # 小于
User.age <= 18             # 小于等于

# 范围
User.age.in_([18, 20, 25])      # 在列表中
User.age.between(18, 30)        # 在范围内
~User.age.in_([18, 20])         # 不在列表中

# 字符串
User.name.like("%张%")          # 模糊匹配（LIKE）
User.name.ilike("%张%")         # 不区分大小写模糊匹配
User.name.startswith("张")      # 以...开头
User.name.endswith("三")        # 以...结尾
User.name.contains("三")        # 包含

# NULL 判断
User.nickname == None           # 是 NULL
User.nickname != None           # 不是 NULL
User.nickname.is_(None)         # 是 NULL（推荐）
User.nickname.is_not(None)      # 不是 NULL
```

### 9.5 排序

```python
# 升序（默认）
stmt = select(News).order_by(News.publish_time)

# 降序
stmt = select(News).order_by(News.views.desc())

# 多字段排序（先按浏览量降序，再按发布时间降序）
stmt = select(News).order_by(
    News.views.desc(),
    News.publish_time.desc()
)
```

### 9.6 分页（offset + limit）

```python
# 第 2 页，每页 10 条
page = 2
page_size = 10
offset = (page - 1) * page_size   # 跳过前 10 条

stmt = select(News).offset(offset).limit(page_size)
result = await session.execute(stmt)
news_list = result.scalars().all()
```

### 9.7 查询指定列（非整个对象）

```python
# 只查询 id 和 title
stmt = select(News.id, News.title)
result = await session.execute(stmt)
rows = result.all()   # 返回元组列表：[(1, "标题1"), (2, "标题2")]

# 使用别名
from sqlalchemy import label
stmt = select(News.id, News.title.label("news_title"))
```

### 9.8 查询实例

> 💡 **掘金头条项目案例**——根据用户名查询用户：
> ```python
> # crud/users.py
> async def get_user_by_username(db: AsyncSession, username: str):
>     query = select(User).where(User.username == username)
>     result = await db.execute(query)
>     return result.scalar_one_or_none()   # 找到返回 User，没找到返回 None
> ```

> 💡 **掘金头条项目案例**——查询新闻列表（带分页和过滤）：
> ```python
> # crud/news_cache.py
> async def get_news_list(db: AsyncSession, category_id: int, skip: int = 0, limit: int = 10):
>     stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
>     result = await db.execute(stmt)
>     news_list = result.scalars().all()
>     return news_list
> ```

> 💡 **掘金头条项目案例**——查询相关新闻（多条件 + 排序 + 排除自己）：
> ```python
> # crud/news_cache.py
> stmt = select(News).where(
>     News.category_id == category_id,    # 同一分类
>     News.id != news_id                   # 排除当前新闻
> ).order_by(
>     News.views.desc(),                   # 按浏览量降序
>     News.publish_time.desc()             # 按发布时间降序
> ).limit(limit)
> ```

---

## 第十章 CRUD 操作——更新（Update）

### 10.1 方式一：修改 ORM 对象属性

```python
# 1. 先查询
user = await session.get(User, 1)   # 按主键获取

# 2. 直接修改属性
user.nickname = "新昵称"
user.bio = "新的个人简介"

# 3. 提交（Session 会自动检测到变化，生成 UPDATE 语句）
await session.commit()
```

**工作原理**：Session 会追踪你修改了哪些属性，commit 时自动生成：
```sql
UPDATE user SET nickname='新昵称', bio='新的个人简介' WHERE id = 1
```

### 10.2 方式二：使用 update() 构造语句

适合**不需要先加载对象**的场景，性能更好：

```python
from sqlalchemy import update

stmt = (
    update(User)
    .where(User.username == "zhangsan")
    .values(nickname="新昵称", bio="新简介")
)
result = await session.execute(stmt)
await session.commit()

# result.rowcount → 被更新的行数
print(f"更新了 {result.rowcount} 条记录")
```

### 10.3 使用 Pydantic 模型驱动更新

```python
async def update_user(db: AsyncSession, username: str, user_data: UserUpdateRequest):
    # user_data 是 Pydantic 模型，model_dump() 转为字典
    # exclude_unset=True → 只包含用户实际传了的字段
    # exclude_none=True → 排除值为 None 的字段
    stmt = (
        update(User)
        .where(User.username == username)
        .values(**user_data.model_dump(exclude_unset=True, exclude_none=True))
    )
    result = await db.execute(stmt)
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="用户不存在")

    updated_user = await get_user_by_username(db, username)
    return updated_user
```

> 💡 **掘金头条项目案例**——更新用户信息（routers/users.py + crud/users.py）：
> ```python
> # crud/users.py
> async def update_user(db: AsyncSession, username: str, user_data: UserUpdateRequest):
>     query = update(User).where(User.username == username).values(
>         **user_data.model_dump(exclude_unset=True, exclude_none=True)
>     )
>     result = await db.execute(query)
>     await db.commit()
>     if result.rowcount == 0:
>         raise HTTPException(status_code=404, detail="用户不存在")
>     updated_user = await get_user_by_username(db, username)
>     return updated_user
> ```

### 10.4 原子更新（在 SQL 层面计算）

适合计数器等场景，不需要先 SELECT 再 UPDATE：

```python
# 浏览量 +1（一条 SQL 搞定，不需要先查再改）
stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
result = await session.execute(stmt)
await session.commit()
```

> 💡 **掘金头条项目案例**——增加新闻浏览量：
> ```python
> # crud/news.py
> async def increase_news_views(db: AsyncSession, news_id: int):
>     stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
>     result = await db.execute(stmt)
>     await db.commit()
>     return result.rowcount > 0   # 检查是否命中了数据
> ```

### 10.5 rowcount 的作用

`result.rowcount` 返回被影响的行数，常用于检查操作是否成功：

```python
result = await session.execute(stmt)
await session.commit()

if result.rowcount == 0:
    # 没有数据被更新 → 说明条件没匹配到
    raise HTTPException(status_code=404, detail="记录不存在")
```

---

## 第十一章 CRUD 操作——删除（Delete）

### 11.1 方式一：删除 ORM 对象

```python
# 1. 先查询
user = await session.get(User, 1)

# 2. 标记删除
session.delete(user)

# 3. 提交
await session.commit()
```

### 11.2 方式二：使用 delete() 构造语句（推荐）

```python
from sqlalchemy import delete

stmt = delete(Favorite).where(
    Favorite.user_id == user_id,
    Favorite.news_id == news_id
)
result = await session.execute(stmt)
await session.commit()

# 检查是否删除成功
return result.rowcount > 0
```

### 11.3 批量删除

```python
# 删除某用户的所有收藏
stmt = delete(Favorite).where(Favorite.user_id == user_id)
result = await session.execute(stmt)
await session.commit()

deleted_count = result.rowcount  # 被删除的行数
```

> 💡 **掘金头条项目案例**——清空历史记录：
> ```python
> # crud/history.py
> async def clear_history(db: AsyncSession, user_id: int):
>     query = delete(History).where(History.user_id == user_id)
>     result = await db.execute(query)
>     await db.commit()
>     return result.rowcount or 0   # 返回删除数量
> ```

---

## 第十二章 关系与外键（Relationships & Foreign Keys）

### 12.1 外键（ForeignKey）

外键用于建立表与表之间的关联关系：

```python
class Favorite(Base):
    __tablename__ = "favorite"

    # user_id 关联到 user 表的 id
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False
    )
    # news_id 关联到 news 表的 id
    news_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("news.id"), nullable=False
    )
```

`ForeignKey("表名.列名")` 格式中，**表名**是数据库中的实际表名（不是类名）。

### 12.2 关系类型

| 关系 | 说明 | 示例 |
|------|------|------|
| 一对一 | 一条记录对应一条记录 | User ↔ Profile |
| 一对多 | 一条记录对应多条记录 | User → Favorite（一个用户多条收藏） |
| 多对多 | 多条记录对应多条记录 | User ↔ News（通过 Favorite 中间表） |

### 12.3 使用 relationship()（可选）

`relationship()` 是 ORM 层面的关联，不会创建数据库列，只在 Python 对象层面建立引用：

```python
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # 一个用户有多条收藏
    favorites = relationship("Favorite", back_populates="user")

class Favorite(Base):
    __tablename__ = "favorite"
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))

    # 反向关联到用户
    user = relationship("User", back_populates="favorites")
```

> 💡 **掘金头条项目** 没有使用 `relationship()`，而是通过手动 JOIN 查询来获取关联数据。这在简单项目中是完全可以的，避免了 relationship 带来的复杂性。

---

## 第十三章 联表查询（JOIN）

### 13.1 基本 JOIN 语法

```python
from sqlalchemy import select

# INNER JOIN：只返回两边都匹配的记录
stmt = (
    select(News, Favorite.created_at)
    .join(Favorite, Favorite.news_id == News.id)
    .where(Favorite.user_id == user_id)
)
result = await session.execute(stmt)
rows = result.all()
# rows = [(News对象, 收藏时间), (News对象, 收藏时间), ...]
```

### 13.2 JOIN 类型

```python
# INNER JOIN（默认）
stmt = select(News).join(Favorite, Favorite.news_id == News.id)

# LEFT OUTER JOIN
from sqlalchemy import outerjoin
stmt = select(News).outerjoin(Favorite, Favorite.news_id == News.id)
```

### 13.3 带别名的 JOIN 查询

```python
stmt = (
    select(
        News,
        Favorite.created_at.label("favorite_time"),
        Favorite.id.label("favorite_id")
    )
    .join(Favorite, Favorite.news_id == News.id)
    .where(Favorite.user_id == user_id)
    .order_by(Favorite.created_at.desc())
    .offset(offset)
    .limit(page_size)
)
result = await session.execute(stmt)
rows = result.all()

# 解包元组
for news, favorite_time, favorite_id in rows:
    print(news.title, favorite_time)
```

> 💡 **掘金头条项目案例**——获取收藏列表（联表查询 + 别名 + 排序 + 分页）：
> ```python
> # crud/favorite.py
> async def get_favorite_list(db, user_id, page=1, page_size=10):
>     # 先查总量
>     count_query = select(func.count()).where(Favorite.user_id == user_id)
>     count_result = await db.execute(count_query)
>     total = count_result.scalar_one()
>
>     # 联表查询
>     offset = (page - 1) * page_size
>     query = (
>         select(News, Favorite.created_at.label("favorite_time"), Favorite.id.label("favorite_id"))
>         .join(Favorite, Favorite.news_id == News.id)
>         .where(Favorite.user_id == user_id)
>         .order_by(Favorite.created_at.desc())
>         .offset(offset).limit(page_size)
>     )
>     result = await db.execute(query)
>     rows = result.all()
>     return rows, total
> ```

---

## 第十四章 异步支持（Asyncio）

### 14.1 为什么需要异步？

在 Web 应用中，数据库查询是**I/O 操作**——CPU 发出请求后需要等待网络响应。

- **同步模式**：等待期间 CPU 什么都不做（浪费资源）
- **异步模式**：等待期间 CPU 可以去处理其他请求（高效）

```
同步：请求A → [等待数据库] → 响应A → 请求B → [等待数据库] → 响应B
异步：请求A → [等待数据库，同时处理请求B] → 响应A → 响应B
```

### 14.2 异步组件一览

| 同步版本 | 异步版本 | 说明 |
|----------|----------|------|
| `create_engine` | `create_async_engine` | 创建引擎 |
| `sessionmaker` | `async_sessionmaker` | 创建 Session 工厂 |
| `Session` | `AsyncSession` | 会话对象 |
| `session.execute()` | `await session.execute()` | 执行查询 |
| `session.commit()` | `await session.commit()` | 提交事务 |
| `session.rollback()` | `await session.rollback()` | 回滚事务 |
| `session.close()` | `await session.close()` | 关闭会话 |
| `session.refresh(obj)` | `await session.refresh(obj)` | 刷新对象 |

### 14.3 异步驱动选择

| 数据库 | 同步驱动 | 异步驱动 |
|--------|----------|----------|
| MySQL | pymysql | aiomysql |
| PostgreSQL | psycopg2 | asyncpg |
| SQLite | sqlite3 | aiosqlite |

### 14.4 完整的异步配置

> 💡 **掘金头条项目案例**——完整的异步数据库配置：
> ```python
> # config/db_conf.py
> from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
>
> # 1. 创建异步引擎
> async_engine = create_async_engine(
>     "mysql+aiomysql://root:123456@localhost:3306/news_app?charset=utf8mb4",
>     echo=True,
>     pool_size=10,
>     max_overflow=20
> )
>
> # 2. 创建异步 Session 工厂
> AsyncSessionLocal = async_sessionmaker(
>     bind=async_engine,
>     class_=AsyncSession,
>     expire_on_commit=False
> )
>
> # 3. 创建依赖注入函数（FastAPI 用）
> async def get_db():
>     async with AsyncSessionLocal() as session:
>         try:
>             yield session
>             await session.commit()
>         except Exception:
>             await session.rollback()
>             raise
>         finally:
>             await session.close()
> ```

### 14.5 在后台任务中使用异步 Session

后台任务（BackgroundTasks）**不能**使用路由里的 db Session，因为路由返回后 Session 就关闭了。需要自己创建：

```python
async def send_welcome_email(user_id: int, email: str):
    # 自己创建 Session，不依赖路由注入
    async with AsyncSessionLocal() as db:
        log = {"user_id": user_id, "type": "welcome"}
        db.add(log)
        await db.commit()
    # async with 结束自动关闭
```

---

## 第十五章 事务管理与 Session 生命周期

### 15.1 事务（Transaction）

事务就是**一组操作，要么全部成功，要么全部失败**。

```python
async def transfer(db: AsyncSession, from_id: int, to_id: int, amount: float):
    # 扣款
    sender = await db.get(Account, from_id)
    sender.balance -= amount

    # 收款
    receiver = await db.get(Account, to_id)
    receiver.balance += amount

    # 提交：两步都成功才写入数据库
    await db.commit()
    # 如果中间出错，get_db 的 except 会执行 rollback()，撤销所有更改
```

### 15.2 Session 状态管理

```python
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session           # ① 路由使用 session
            await session.commit()  # ② 成功：提交
        except Exception:
            await session.rollback() # ③ 失败：回滚
            raise                    # ④ 重新抛出异常
        finally:
            await session.close()    # ⑤ 无论如何：关闭
```

**为什么这样设计？**
- 步骤 ② 保证：路由正常返回时，所有更改才会写入数据库
- 步骤 ③ 保证：任何错误都不会导致"脏数据"写入
- 步骤 ⑤ 保证：连接一定被归还到连接池

### 15.3 手动控制 commit

在某些场景下，你可能想在 CRUD 函数内部手动 commit：

```python
async def create_user(db: AsyncSession, user_data: UserRequest):
    user = User(username=user_data.username, password="xxx")
    db.add(user)
    await db.commit()      # 手动提交（获取自动生成的 id）
    await db.refresh(user) # 刷新对象
    return user
```

⚠️ 注意：如果 `get_db` 里也有 `commit()`，那实际上会 commit 两次。但 SQLAlchemy 足够聪明——如果没有新的更改，第二次 commit 什么都不会做。

---

## 第十六章 ORM 对象的状态流转

### 16.1 四种状态

SQLAlchemy 中的 ORM 对象有四种状态：

```
┌──────────┐   add()    ┌──────────┐   flush()   ┌──────────┐
│ Transient │ ────────→ │ Pending  │ ──────────→ │ Persistent│
│ (瞬态)    │           │ (待插入)  │  commit()   │ (持久化)   │
└──────────┘           └──────────┘             └─────┬────┘
                                                      │
                                                      │ close()
                                                      ▼
                                                ┌──────────┐
                                                │ Detached │
                                                │ (分离)    │
                                                └──────────┘
```

| 状态 | 说明 | 特征 |
|------|------|------|
| **Transient**（瞬态） | 刚创建的对象，还没有被 Session 管理 | `id` 为 None，不在 Session 中 |
| **Pending**（待插入） | 已 add 到 Session，但还没 flush | 在 `session.new` 中 |
| **Persistent**（持久化） | 已写入数据库，被 Session 管理 | 有 `id`，在 Session 中 |
| **Detached**（分离） | 从 Session 中脱离（比如 Session 关闭后） | 有 `id`，但不在 Session 中 |

### 16.2 状态检查

```python
from sqlalchemy import inspect

user = User(username="test")
insp = inspect(user)

print(insp.transient)     # True → 瞬态
print(insp.pending)       # False
print(insp.persistent)    # False
print(insp.detached)      # False

session.add(user)
print(insp.pending)       # True → 待插入

await session.commit()
print(insp.persistent)    # True → 持久化

await session.close()
print(insp.detached)      # True → 分离
```

### 16.3 为什么这很重要？

**分离状态的对象不能直接操作数据库！** 这就是为什么后台任务不能传路由的 db：

```python
# ❌ 错误：路由返回后 session 关闭，db 是分离状态
async def background_task(db: AsyncSession, user_id: int):
    db.add(something)        # 💥 Session 已关闭！
    await db.commit()        # 💥 Session 已关闭！

# ✅ 正确：自己创建 Session
async def background_task(user_id: int):
    async with AsyncSessionLocal() as db:
        db.add(something)
        await db.commit()
```

---

## 第十七章 聚合函数与分组

### 17.1 常用聚合函数

```python
from sqlalchemy import func

# COUNT：计数
stmt = select(func.count(News.id)).where(News.category_id == 1)
result = await session.execute(stmt)
count = result.scalar_one()

# SUM：求和
stmt = select(func.sum(Order.amount))

# AVG：平均值
stmt = select(func.avg(Product.price))

# MAX / MIN：最大/最小值
stmt = select(func.max(News.views))
```

### 17.2 COUNT 查询

> 💡 **掘金头条项目案例**——获取新闻数量：
> ```python
> # crud/news_cache.py
> async def get_news_count(db: AsyncSession, category_id: int):
>     stmt = select(func.count(News.id)).where(News.category_id == category_id)
>     result = await db.execute(stmt)
>     return result.scalar_one()   # 返回整数
> ```

> 💡 **掘金头条项目案例**——获取收藏总量：
> ```python
> # crud/favorite.py
> count_query = select(func.count()).where(Favorite.user_id == user_id)
> count_result = await db.execute(count_query)
> total = count_result.scalar_one()
> ```

### 17.3 分组（GROUP BY）

```python
from sqlalchemy import func

# 按分类统计新闻数量
stmt = (
    select(News.category_id, func.count(News.id).label("total"))
    .group_by(News.category_id)
)
result = await session.execute(stmt)
for row in result:
    print(f"分类 {row.category_id}: {row.total} 条新闻")
```

### 17.4 HAVING（分组后过滤）

```python
# 筛选出新闻数量大于 10 的分类
stmt = (
    select(News.category_id, func.count(News.id).label("total"))
    .group_by(News.category_id)
    .having(func.count(News.id) > 10)
)
```

---

## 第十八章 项目实战总结

### 18.1 CRUD 操作速查表

| 操作 | SQLAlchemy 2.0 写法 |
|------|---------------------|
| **创建** | `db.add(obj)` → `await db.commit()` → `await db.refresh(obj)` |
| **查询全部** | `select(Model)` → `result.scalars().all()` |
| **条件查询** | `select(Model).where(Model.field == value)` |
| **主键查询** | `await db.get(Model, id)` |
| **查询一条** | `result.scalar_one_or_none()` |
| **分页** | `.offset(skip).limit(size)` |
| **排序** | `.order_by(Model.field.desc())` |
| **计数** | `select(func.count(Model.id))` |
| **更新** | `update(Model).where(...).values(...)` |
| **删除** | `delete(Model).where(...)` |
| **联表** | `select(A, B).join(B, B.a_id == A.id).where(...)` |

### 18.2 常见错误与解决

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `DetachedInstanceError` | 对象从 Session 脱离后访问属性 | 使用 `expire_on_commit=False` 或在 Session 有效期内访问 |
| `MissingGreenlet` | 在异步环境使用了同步操作 | 确保所有操作都用 `await` |
| `Statement is not a query` | execute 传入的不是 Statement | 检查是否忘了用 `select()` 等构造语句 |
| `Instance is not bound` | Session 已关闭后操作 | 确保在 `async with` 块内操作 |
| 多个 Base 导致表未创建 | 不同 Base 有不同的 metadata | 全项目共用一个 Base |

### 18.3 掘金头条项目数据流图

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Router                        │
│  routers/news.py, routers/users.py, ...                 │
│                                                         │
│  async def get_news_list(db = Depends(get_db)):         │
│      └→ 调用 crud 层方法                                 │
├─────────────────────────────────────────────────────────┤
│                      CRUD 层                             │
│  crud/news_cache.py, crud/users.py, ...                 │
│                                                         │
│  ① 先查缓存                                              │
│  ② 缓存未命中 → 用 SQLAlchemy 查数据库                    │
│  ③ 写入缓存                                              │
│  ④ 返回 ORM 对象                                         │
├─────────────────────────────────────────────────────────┤
│                    Models 层                             │
│  models/news.py, models/users.py, ...                   │
│                                                         │
│  News, Category, User, UserToken, Favorite, History     │
├─────────────────────────────────────────────────────────┤
│                   Session 层                             │
│  config/db_conf.py → get_db()                           │
│                                                         │
│  async_engine → AsyncSessionLocal → AsyncSession        │
├─────────────────────────────────────────────────────────┤
│                    数据库                                 │
│  MySQL (news_app)                                       │
└─────────────────────────────────────────────────────────┘
```

### 18.4 最佳实践清单

1. **全项目共用一个 Base**——避免 `metadata` 分裂
2. **使用 `expire_on_commit=False`**——避免 commit 后对象属性过期
3. **后台任务自己创建 Session**——不要传路由的 db 进去
4. **优先用 `update()` / `delete()` 构造语句**——不需要先加载对象
5. **使用 `rowcount` 检查操作是否成功**——比 `try/except` 更精确
6. **给高频查询列建索引**——提升查询性能
7. **使用 `label()` 给联表查询的列起别名**——解包元组更方便
8. **使用 `scalar_one_or_none()` 处理"有或没有"的查询**——比 `one()` 更安全
