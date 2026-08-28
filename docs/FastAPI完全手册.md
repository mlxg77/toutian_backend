# FastAPI 完全学习手册

> 本手册基于 FastAPI 官方文档整理，结合「掘金头条」后端项目（toutiao_backend）的实际代码作为案例。
> 适合零基础小白从头学起，从基础到进阶全面覆盖。

---

## 目录

- [第一章 FastAPI 简介与安装](#第一章-fastapi-简介与安装)
- [第二章 第一个 FastAPI 应用](#第二章-第一个-fastapi-应用)
- [第三章 路由（Path Operation）](#第三章-路由path-operation)
- [第四章 路径参数（Path Parameters）](#第四章-路径参数path-parameters)
- [第五章 查询参数（Query Parameters）](#第五章-查询参数query-parameters)
- [第六章 请求体（Request Body）与 Pydantic](#第六章-请求体request-body与-pydantic)
- [第七章 响应模型（Response Model）](#第七章-响应模型response-model)
- [第八章 路由组织与 APIRouter](#第八章-路由组织与-apirouter)
- [第九章 依赖注入（Dependency Injection）](#第九章-依赖注入dependency-injection)
- [第十章 中间件（Middleware）](#第十章-中间件middleware)
- [第十一章 CORS 跨域资源共享](#第十一章-cors-跨域资源共享)
- [第十二章 异常处理（Exception Handling）](#第十二章-异常处理exception-handling)
- [第十三章 后台任务（Background Tasks）](#第十三章-后台任务background-tasks)
- [第十四章 JSON 编码工具 jsonable_encoder](#第十四章-json-编码工具-jsonable_encoder)
- [第十五章 Header 参数与自定义响应](#第十五章-header-参数与自定义响应)
- [第十六章 生命周期事件（Lifespan Events）](#第十六章-生命周期事件lifespan-events)
- [第十七章 项目架构与最佳实践](#第十七章-项目架构与最佳实践)

---

## 第一章 FastAPI 简介与安装

### 1.1 什么是 FastAPI？

FastAPI 是一个用于构建 API 的**现代、高性能** Python Web 框架。它的核心特点：

| 特点 | 说明 |
|------|------|
| **快速** | 性能与 NodeJS、Go 相当，是 Python 最快的 Web 框架之一 |
| **快速编码** | 将开发速度提升 200%~300% |
| **更少的 Bug** | 减少约 40% 的人为错误 |
| **直观** | 强大的编辑器支持（自动补全、类型检查），减少调试时间 |
| **简单** | 设计为易于学习和使用，减少阅读文档的时间 |
| **短** | 最小化代码重复，一个参数声明可以实现多种功能 |
| **健壮** | 自动生成交互式 API 文档 |
| **基于标准** | 基于 OpenAPI 和 JSON Schema 等开放标准 |

### 1.2 FastAPI 的技术基础

FastAPI 站在巨人的肩膀上：

- **Starlette**：提供 Web 部分（路由、中间件、请求/响应、CORS 等）
- **Pydantic**：提供数据验证部分（数据校验、序列化、类型转换）
- **Uvicorn**：ASGI 服务器，负责运行 FastAPI 应用

```
┌──────────────────────────────────┐
│          FastAPI 应用             │
├──────────────┬───────────────────┤
│   Starlette  │     Pydantic      │
│  (Web 部分)  │   (数据验证部分)    │
├──────────────┴───────────────────┤
│           Uvicorn               │
│       (ASGI 服务器)              │
└──────────────────────────────────┘
```

### 1.3 安装

**方式一：使用 pip（推荐初学者）**

```bash
# 1. 创建并激活虚拟环境
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
# source .venv/bin/activate

# 2. 安装 FastAPI 和 Uvicorn
pip install "fastapi[standard]"
```

**方式二：使用 uv（推荐现代项目）**

```bash
uv init my-project --bare
cd my-project
uv add "fastapi[standard]"
```

> 💡 **掘金头条项目** 使用 pip + requirements.txt 管理依赖，FastAPI 版本为 0.125.0。

---

## 第二章 第一个 FastAPI 应用

### 2.1 最简应用

创建 `main.py`：

```python
from fastapi import FastAPI

# 创建 FastAPI 应用实例
app = FastAPI()

# 定义一个路由（路径操作）
@app.get("/")
async def root():
    return {"message": "Hello World"}
```

### 2.2 运行应用

```bash
# 开发模式（支持热重载，代码修改后自动重启）
fastapi dev main.py

# 或者使用 uvicorn 直接运行
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**参数解释：**

| 参数 | 说明 |
|------|------|
| `main` | Python 文件名（不含 .py） |
| `app` | main.py 中的 FastAPI 实例名 |
| `--reload` | 开发模式，文件修改后自动重启 |
| `--host` | 监听地址，0.0.0.0 表示所有网络接口 |
| `--port` | 监听端口，默认 8000 |

### 2.3 自动生成的 API 文档

运行后访问以下地址，即可看到自动生成的交互式 API 文档：

- **Swagger UI**：http://127.0.0.1:8000/docs
- **ReDoc**：http://127.0.0.1:8000/redoc

> 💡 这两个文档是 FastAPI 自动生成的，不需要你写任何额外的代码！这就是 FastAPI "基于标准"的好处——它遵循 OpenAPI 规范，自动生成文档。

### 2.4 同步 vs 异步

FastAPI 同时支持 `def` 和 `async def`：

```python
# 异步函数（推荐用于 I/O 密集型操作：数据库查询、HTTP 请求等）
@app.get("/async-example")
async def async_example():
    return {"message": "这是异步的"}

# 同步函数（适合 CPU 密集型操作，FastAPI 会自动放到线程池中执行）
@app.get("/sync-example")
def sync_example():
    return {"message": "这是同步的"}
```

**如何选择？**
- 如果你的函数需要用 `await`（比如异步数据库操作），就用 `async def`
- 如果你不确定，或者函数里有很多计算，就用普通的 `def`
- 在同一个应用中可以混用两者

> 💡 **掘金头条项目** 全程使用 `async def`，因为项目中使用了 SQLAlchemy 的异步引擎和 Redis 异步客户端。

---

## 第三章 路由（Path Operation）

### 3.1 什么是路由 / 路径操作？

在 FastAPI 中，**路径操作（Path Operation）** 就是你为某个 URL 路径 + HTTP 方法组合编写的处理函数。

```
HTTP 方法 + URL 路径 → 处理函数（Path Operation Function）
```

常见的 HTTP 方法及其用途：

| HTTP 方法 | 用途 | 是否有请求体 |
|-----------|------|-------------|
| `GET` | 获取数据 | 通常没有 |
| `POST` | 创建数据 | 通常有 |
| `PUT` | 更新数据（全量） | 有 |
| `PATCH` | 更新数据（部分） | 有 |
| `DELETE` | 删除数据 | 通常没有 |

### 3.2 定义路由

使用**装饰器**来定义路由：

```python
from fastapi import FastAPI

app = FastAPI()

# GET 请求：获取数据
@app.get("/items")
async def read_items():
    return [{"name": "Item 1"}, {"name": "Item 2"}]

# POST 请求：创建数据
@app.post("/items")
async def create_item():
    return {"message": "Item created"}

# PUT 请求：更新数据
@app.put("/items/{item_id}")
async def update_item(item_id: int):
    return {"message": f"Item {item_id} updated"}

# DELETE 请求：删除数据
@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    return {"message": f"Item {item_id} deleted"}
```

### 3.3 路径操作装饰器的参数

```python
@app.get(
    "/items",
    summary="获取商品列表",           # 简短摘要
    description="获取所有商品的列表，支持分页",  # 详细描述
    response_description="返回商品列表",    # 响应描述
    deprecated=False,               # 是否标记为废弃
    tags=["商品管理"]                 # 分组标签
)
async def read_items():
    return []
```

> 💡 **掘金头条项目案例**——新闻详情接口：
> ```python
> # routers/news.py
> @router.get("/detail")
> async def get_news_detail(news_id: int = Query(..., alias="id"), db: AsyncSession = Depends(get_db)):
>     news_detail = await news_cache.get_news_detail(db, news_id)
>     if not news_detail:
>         raise HTTPException(status_code=404, detail="新闻不存在")
>     ...
> ```

---

## 第四章 路径参数（Path Parameters）

### 4.1 基础用法

路径参数就是 URL 路径中的变量部分，用 `{参数名}` 表示：

```python
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```

当你访问 `/items/3` 时，`item_id` 的值就是 `3`。

**关键点：**
- 函数参数名必须与路径中的变量名**完全一致**（`item_id`）
- FastAPI 会自动进行**类型验证**——如果你传 `"foo"` 而不是整数，会返回一个友好的错误

### 4.2 类型验证

```python
# item_id 必须是 int 类型
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

# 访问 /items/3 → 正常返回 {"item_id": 3}
# 访问 /items/foo → 自动返回 422 错误，告诉你 item_id 应该是整数
```

### 4.3 使用 Pydantic 约束路径参数

```python
from enum import Enum
from fastapi import FastAPI, Path

app = FastAPI()

# 方式一：使用 Enum 限制取值范围
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    return {"model": model_name, "message": f"选择了 {model_name.value}"}

# 方式二：使用 Path() 添加验证规则
@app.get("/items/{item_id}")
async def read_item(
    item_id: int = Path(
        ...,            # ... 表示这是必填参数
        ge=1,           # 大于等于 1
        le=1000,        # 小于等于 1000
        title="商品ID",
        description="商品的唯一标识符"
    )
):
    return {"item_id": item_id}
```

### 4.4 包含路径的路径参数

如果你需要匹配包含 `/` 的路径（比如文件路径），可以使用 `path` 转换器：

```python
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}
# 访问 /files/home/user/file.txt → file_path = "home/user/file.txt"
```

> 💡 **掘金头条项目案例**——删除历史记录接口使用了路径参数：
> ```python
> # routers/history.py
> @router.delete("/delete/{history_id}")
> async def delete_history(history_id: int,
>                          user: User = Depends(get_current_user),
>                          db: AsyncSession = Depends(get_db)):
>     result = await history.delete_history(db, user.id, history_id)
>     ...
> ```
> 这里 `history_id` 是路径参数，FastAPI 会自动从 URL 中 `/api/history/delete/5` 提取出 `5`。

---

## 第五章 查询参数（Query Parameters）

### 5.1 基础用法

**查询参数**就是 URL 中 `?` 后面的键值对，例如：
```
GET /items?skip=0&limit=10
```

在 FastAPI 中，只要函数参数**不是**路径参数，且类型是**简单类型**（`str`、`int`、`bool` 等），FastAPI 就会自动把它当作查询参数：

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items")
async def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
# GET /items?skip=5&limit=20 → {"skip": 5, "limit": 20}
# GET /items → {"skip": 0, "limit": 10}（使用默认值）
```

### 5.2 必填与可选参数

```python
@app.get("/items")
async def read_items(
    q: str,                        # 没有默认值 → 必填
    skip: int = 0,                 # 有默认值 → 可选
    limit: int = 10                # 有默认值 → 可选
):
    return {"q": q, "skip": skip, "limit": limit}
```

### 5.3 使用 Query() 添加验证和元数据

`Query()` 是 FastAPI 提供的工具，用于给查询参数添加**额外的验证规则**和**文档信息**：

```python
from fastapi import Query

@app.get("/items")
async def read_items(
    q: str = Query(
        ...,                    # ... 表示必填
        min_length=3,           # 最小长度
        max_length=50,          # 最大长度
        pattern="^search_",     # 正则表达式验证（必须以 search_ 开头）
        title="搜索关键词",      # 文档标题
        description="用于搜索的关键词"  # 文档描述
    ),
    page: int = Query(1, ge=1),           # 最小值为 1
    page_size: int = Query(10, ge=1, le=100)  # 1~100 之间
):
    return {"q": q, "page": page, "page_size": page_size}
```

### 5.4 参数别名（alias）

当前端传的字段名和 Python 变量名不一致时，可以使用 `alias`：

```python
@app.get("/news")
async def get_news(
    category_id: int = Query(..., alias="categoryId"),   # 前端传 categoryId
    page_size: int = Query(10, alias="pageSize")         # 前端传 pageSize
):
    return {"category_id": category_id, "page_size": page_size}
# GET /news?categoryId=1&pageSize=20
# Python 函数内部使用 category_id 和 page_size
```

> 💡 **掘金头条项目案例**——新闻列表接口使用了大量 Query 参数：
> ```python
> # routers/news.py
> @router.get("/list")
> async def get_news_list(
>         category_id: int = Query(..., alias="categoryId"),      # 必填，前端传 categoryId
>         page: int = 1,                                          # 可选，默认值 1
>         page_size: int = Query(10, alias="pageSize", le=100),   # 可选，最大 100
>         db: AsyncSession = Depends(get_db)                      # 数据库依赖注入
> ):
>     offset = (page - 1) * page_size
>     news_list = await news_cache.get_news_list(db, category_id, offset, page_size)
>     ...
> ```

### 5.5 接收多个值（列表参数）

```python
from typing import List

@app.get("/items")
async def read_items(q: List[str] = Query(None)):
    return {"q": q}
# GET /items?q=foo&q=bar&q=baz → {"q": ["foo", "bar", "baz"]}
```

---

## 第六章 请求体（Request Body）与 Pydantic

### 6.1 什么是请求体？

当客户端（浏览器/手机 App）向服务器**发送数据**时，数据通常放在请求体（Body）中。请求体一般配合 `POST`、`PUT`、`PATCH` 方法使用。

### 6.2 使用 Pydantic 定义请求体

Pydantic 是 Python 的数据验证库。FastAPI 用 Pydantic 模型来声明请求体的格式：

```python
from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()

# 第一步：定义 Pydantic 模型（继承 BaseModel）
class Item(BaseModel):
    name: str                    # 必填字符串
    description: str | None = None   # 可选字符串
    price: float                 # 必填浮点数
    tax: float | None = None     # 可选浮点数

# 第二步：在路由函数中使用
@app.post("/items")
async def create_item(item: Item):  # item 的类型是 Item
    # FastAPI 会自动做以下事情：
    # 1. 读取请求体中的 JSON
    # 2. 转换为对应的 Python 类型
    # 3. 验证数据是否符合模型定义
    # 4. 如果数据无效，返回 422 错误
    return item
    # 你也可以访问属性：item.name, item.price 等
```

### 6.3 Pydantic 模型详解

#### 6.3.1 基础字段类型

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserModel(BaseModel):
    # 基础类型
    username: str                              # 必填字符串
    age: int                                   # 必填整数
    score: float                               # 必填浮点数
    is_active: bool                            # 必填布尔值

    # 可选字段（有默认值的字段不是必填的）
    nickname: Optional[str] = None             # 可选字符串
    bio: str = "这个人很懒"                      # 有默认值

    # 使用 Field() 添加验证规则
    password: str = Field(
        ...,                                   # ... 表示必填
        min_length=6,                          # 最小 6 个字符
        max_length=128,                        # 最大 128 个字符
        description="用户密码"
    )
```

#### 6.3.2 使用 Field() 添加约束

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="商品名称")
    price: float = Field(..., gt=0, le=99999, description="价格必须大于 0 且不超过 99999")
    quantity: int = Field(0, ge=0, description="库存数量不能为负")
    # Field 的常用约束参数：
    # gt  = 大于        ge = 大于等于
    # lt  = 小于        le = 小于等于
    # min_length = 最小长度    max_length = 最大长度
    # pattern = 正则表达式     description = 描述
```

#### 6.3.3 字段别名（alias）

前端用驼峰命名（`camelCase`），后端用蛇形命名（`snake_case`）时，使用 `alias` 做映射：

```python
from pydantic import BaseModel, Field, ConfigDict

class UserRequest(BaseModel):
    old_password: str = Field(..., alias="oldPassword")
    new_password: str = Field(..., min_length=6, alias="newPassword")
```

> 💡 **掘金头条项目案例**——修改密码请求模型：
> ```python
> # schemas/users.py
> class UserChangePasswordRequest(BaseModel):
>     old_password: str = Field(..., alias="oldPassword", description="旧密码")
>     new_password: str = Field(..., min_length=6, alias="newPassword", description="新密码")
> ```

### 6.4 请求体 + 路径参数 + 查询参数同时使用

FastAPI 能自动区分参数来源：

```python
from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.put("/items/{item_id}")
async def update_item(
    item_id: int,        # 在路径中声明 → 路径参数
    item: Item,          # Pydantic 模型 → 请求体
    q: str | None = None # 简单类型 + 有默认值 → 查询参数
):
    return {"item_id": item_id, **item.model_dump(), "q": q}
# PUT /items/5?q=hello
# Body: {"name": "Widget", "price": 9.99}
# → {"item_id": 5, "name": "Widget", "price": 9.99, "q": "hello"}
```

**FastAPI 的参数识别规则：**

| 参数类型 | 识别方式 |
|---------|---------|
| 路径参数 | 参数名在路径 `{xxx}` 中出现 |
| 请求体 | 参数类型是 Pydantic 模型 |
| 查询参数 | 简单类型（str、int、bool 等），且不在路径中 |

### 6.5 model_config 配置

Pydantic v2 使用 `model_config` 来配置模型行为：

```python
from pydantic import BaseModel, ConfigDict

class UserInfoResponse(BaseModel):
    id: int
    username: str
    nickname: str | None = None

    model_config = ConfigDict(
        from_attributes=True,    # 允许从 ORM 对象属性中取值（而非字典）
        populate_by_name=True    # 同时支持字段名和别名赋值
    )
```

| 配置项 | 说明 |
|--------|------|
| `from_attributes=True` | 允许用 `model_validate(orm_obj)` 将 ORM 对象转为 Pydantic 模型 |
| `populate_by_name=True` | 构造模型时既可以用字段名，也可以用别名 |
| `str_strip_whitespace=True` | 自动去除字符串两端的空格 |

> 💡 **掘金头条项目案例**——`populate_by_name` 的使用场景：
> ```python
> # schemas/users.py
> class UserAuthResponse(BaseModel):
>     token: str
>     user_info: UserInfoResponse = Field(..., alias="userInfo")
>
>     model_config = ConfigDict(
>         populate_by_name=True,   # 让 user_info=xxx 和 userInfo=xxx 都能用
>         from_attributes=True
>     )
> ```

### 6.6 模型继承

Pydantic 模型支持继承，子类可以复用父类的字段并添加新字段：

```python
class NewsItemBase(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    author: Optional[str] = None
    category_id: int = Field(alias="categoryId")
    views: int
    publish_time: Optional[datetime] = Field(None, alias="publishTime")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# 继承 NewsItemBase，新增 content 和 related_news 字段
class NewsDetailResponse(NewsItemBase):
    content: str
    related_news: list[RelatedNewsResponse] = Field(default_factory=list, alias="relatedNews")
```

> 💡 **掘金头条项目**的 schemas 就大量使用了继承：
> - `schemas/base.py` 中的 `NewsItemBase` 是基础新闻模型
> - `schemas/news.py` 中的 `NewsDetailResponse` 继承了 `NewsItemBase`，新增了 `content` 字段
> - `schemas/favorite.py` 中的 `FavoriteNewsItemResponse` 继承了 `NewsItemBase`，新增了收藏时间和 ID

---

## 第七章 响应模型（Response Model）

### 7.1 为什么需要响应模型？

响应模型的作用：
1. **数据过滤**：只返回需要的字段（比如密码字段不应该返回给前端）
2. **数据转换**：自动将 ORM 对象转换为 JSON
3. **文档生成**：在 Swagger UI 中展示响应格式

### 7.2 声明响应模型

```python
from pydantic import BaseModel, EmailStr
from fastapi import FastAPI

app = FastAPI()

class UserIn(BaseModel):
    username: str
    password: str       # 输入时有密码
    email: str

class UserOut(BaseModel):
    username: str
    email: str          # 输出时没有密码！

@app.post("/users", response_model=UserOut)
async def create_user(user: UserIn):
    # 模拟保存用户（实际项目中还要加密密码）
    return user  # FastAPI 会自动过滤掉 password 字段
```

### 7.3 手动构造响应数据

在实际项目中，我们通常不直接用 `response_model`，而是手动构造返回的数据。掘金头条项目就是这种方式——通过 `success_response()` 函数统一封装响应格式：

```python
# utils/response.py
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

def success_response(message: str = "success", data=None):
    content = {
        "code": 200,
        "message": message,
        "data": data
    }
    # jsonable_encoder：把任何 Python 对象转换为 JSON 兼容的字典
    return JSONResponse(content=jsonable_encoder(content))
```

这样所有接口的响应格式统一为：
```json
{
    "code": 200,
    "message": "获取新闻列表成功",
    "data": { ... }
}
```

### 7.4 model_validate 与 model_dump

Pydantic v2 中两个核心方法：

```python
# model_validate：将其他对象（ORM 对象、字典）转换为 Pydantic 模型
user_pydantic = UserInfoResponse.model_validate(user_orm_object)
# 需要模型配置 from_attributes=True 才能处理 ORM 对象

# model_dump：将 Pydantic 模型转换为字典
user_dict = user_pydantic.model_dump()
# 参数：
#   by_alias=True   → 使用别名作为 key（"categoryId" 而非 "category_id"）
#   by_alias=False  → 使用字段名作为 key
#   mode="json"     → 确保值是 JSON 兼容类型（datetime → 字符串）
#   exclude={'field'} → 排除某些字段
#   exclude_unset=True → 只包含被显式设置过的字段
#   exclude_none=True  → 排除值为 None 的字段
```

> 💡 **掘金头条项目案例**——ORM 对象转 Pydantic 再转字典的完整流程：
> ```python
> # crud/news_cache.py 中缓存新闻列表时：
> # 1. ORM → Pydantic（model_validate）
> # 2. Pydantic → JSON 兼容字典（model_dump）
> news_data = [
>     NewsItemBase.model_validate(item).model_dump(mode="json", by_alias=False)
>     for item in news_list
> ]
> # 3. 存入 Redis 缓存
> await set_cache_news_list(category_id, page, limit, news_data)
> ```

---

## 第八章 路由组织与 APIRouter

### 8.1 为什么需要路由组织？

当项目变大后，所有路由都写在 `main.py` 中会变得非常混乱。FastAPI 提供了 `APIRouter` 来**按模块拆分路由**。

### 8.2 基础用法

```python
# routers/news.py
from fastapi import APIRouter

# 创建路由器实例
router = APIRouter(
    prefix="/api/news",    # 所有路由的 URL 前缀
    tags=["新闻管理"]       # Swagger 文档中的分组标签
)

@router.get("/list")        # 实际 URL: /api/news/list
async def get_news_list():
    return {"news": []}

@router.get("/detail")      # 实际 URL: /api/news/detail
async def get_news_detail():
    return {"detail": {}}
```

```python
# main.py
from fastapi import FastAPI
from routers import news, users

app = FastAPI()

# 注册路由（挂载）
app.include_router(news.router)
app.include_router(users.router)
```

### 8.3 APIRouter 的参数详解

```python
router = APIRouter(
    prefix="/api/users",          # URL 前缀
    tags=["用户管理"],             # 文档标签
    dependencies=[Depends(auth)], # 该模块所有路由的公共依赖
    responses={404: {"description": "Not found"}}  # 公共响应
)
```

### 8.4 路由嵌套（Router of Routers）

大型项目可以把路由分组：

```python
# main.py
from fastapi import APIRouter, FastAPI

app = FastAPI()

# 创建 "用户相关" 的父路由器
user_router = APIRouter(prefix="/user")

# 把子路由器挂载到父路由器
user_router.include_router(auth_router)      # /user/auth/...
user_router.include_router(profile_router)   # /user/profile/...

# 再把父路由器挂载到 app
app.include_router(user_router)
```

> 💡 **掘金头条项目的路由组织：**
> ```
> main.py
> ├── routers/news.py       → prefix="/api/news"      tags=["news"]
> ├── routers/users.py      → prefix="/api/user"      tags=["users"]
> ├── routers/favorite.py   → prefix="/api/favorite"  tags=["favorite"]
> └── routers/history.py    → prefix="/api/history"   tags=["history"]
> ```
> 每个模块一个路由文件，通过 `include_router` 统一注册到主应用。

---

## 第九章 依赖注入（Dependency Injection）

### 9.1 什么是依赖注入？

**依赖注入**是 FastAPI 最强大的特性之一。简单理解：

> 当一个函数需要某些东西（数据库连接、当前用户等）才能工作时，FastAPI 会**自动帮你准备好**这些东西，然后"注入"到函数参数中。

你不需要手动调用函数来获取这些依赖，FastAPI 会替你管理。

### 9.2 基础用法：Depends()

```python
from fastapi import Depends

# 定义一个依赖函数
async def common_parameters(
    skip: int = 0,
    limit: int = 100,
    q: str | None = None
):
    return {"skip": skip, "limit": limit, "q": q}

# 在路由中使用 Depends() 注入依赖
@app.get("/items")
async def read_items(params: dict = Depends(common_parameters)):
    return params
```

### 9.3 数据库会话依赖

这是最常见的依赖注入场景——为每个请求创建数据库连接，请求结束后自动关闭：

```python
# config/db_conf.py
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

async_engine = create_async_engine("mysql+aiomysql://root:123456@localhost:3306/news_app")
AsyncSessionLocal = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session           # 把 session 交给路由使用
            await session.commit()  # 路由正常执行后提交事务
        except Exception:
            await session.rollback()  # 出错时回滚
            raise
        finally:
            await session.close()     # 无论如何都关闭连接
```

```python
# 在路由中使用
from config.db_conf import get_db

@router.get("/list")
async def get_news_list(db: AsyncSession = Depends(get_db)):
    # db 就是 get_db() 中 yield 出来的 session
    news_list = await news_cache.get_news_list(db, ...)
    return success_response(data=news_list)
```

**`yield` 的关键作用：**
1. `yield` 之前的代码 → 请求开始时执行（创建连接）
2. `yield` 把值交给路由函数使用
3. 路由函数执行完毕后 → `yield` 之后的代码执行（清理资源）

### 9.4 认证依赖（依赖链）

依赖可以嵌套——一个依赖可以使用另一个依赖：

```python
# utils/auth.py
from fastapi import Header, Depends, HTTPException

async def get_current_user(
        authorization: str = Header(..., alias="Authorization"),   # 依赖1：从请求头取 Token
        db: AsyncSession = Depends(get_db)                         # 依赖2：获取数据库连接
):
    # authorization 的值类似 "Bearer abc123"
    token = authorization.replace("Bearer ", "")
    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="无效的令牌或已经过期的令牌")
    return user
```

```python
# 在路由中使用
@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
    # user 就是 get_current_user() 返回的 User 对象
    return success_response(data=UserInfoResponse.model_validate(user))

@router.put("/update")
async def update_user_info(
    user_data: UserUpdateRequest,
    user: User = Depends(get_current_user),     # 注入当前用户
    db: AsyncSession = Depends(get_db)           # 注入数据库连接
):
    ...
```

**依赖链的执行顺序：**
```
请求进入
  → FastAPI 执行 get_db()，创建数据库连接
  → FastAPI 执行 get_current_user()（内部也用到了 get_db）
  → 路由函数拿到 user 和 db，执行业务逻辑
  → 路由返回响应
  → get_db() 的 yield 之后代码执行，关闭连接
```

### 9.5 依赖注入的好处

| 好处 | 说明 |
|------|------|
| **代码复用** | 同一个依赖可以被多个路由复用 |
| **关注点分离** | 认证逻辑和数据库逻辑与业务逻辑解耦 |
| **易于测试** | 测试时可以替换（mock）依赖 |
| **自动管理** | FastAPI 自动处理依赖的生命周期（创建和清理） |

> 💡 **为什么不用普通函数调用？**
> ```python
> # ❌ 直接调用函数——技术上可行，但丢失了 Depends 的好处
> async def get_user_info():
>     db = await get_db()          # 手动管理连接
>     user = await get_current_user(db)  # 手动传参
>     ...
>
> # ✅ 使用依赖注入——FastAPI 自动管理一切
> async def get_user_info(user: User = Depends(get_current_user)):
>     ...
> ```
> 直接调用函数会把 Depends 帮你解决的 3 件事（参数复用、测试 mock、缓存）全打回原形。

---

## 第十章 中间件（Middleware）

### 10.1 什么是中间件？

中间件是一个在**每个请求到达路由之前**和**每个响应返回之前**都会执行的函数。

```
请求 → 中间件1 → 中间件2 → 路由函数
响应 ← 中间件1 ← 中间件2 ← 路由函数
```

### 10.2 自定义中间件

```python
import time
from fastapi import FastAPI, Request

app = FastAPI()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    # ---- 请求到达路由之前 ----
    start_time = time.perf_counter()

    # 把请求传递给下一个中间件或路由
    response = await call_next(request)

    # ---- 响应返回之前 ----
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    return response
```

**关键理解：**
- `call_next(request)` 把请求传递给下一个环节
- `call_next` 之前的代码 → 请求处理前执行
- `call_next` 之后的代码 → 响应返回前执行

### 10.3 多个中间件的执行顺序

```python
app.add_middleware(MiddlewareA)
app.add_middleware(MiddlewareB)
```

执行顺序：
```
请求：MiddlewareB → MiddlewareA → 路由
响应：路由 → MiddlewareA → MiddlewareB
```

**最后添加的中间件在最外层**，最先处理请求，最后处理响应。

### 10.4 常用内置中间件

```python
# CORS 中间件（详见下一章）
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)

# GZip 压缩中间件（压缩响应数据）
from starlette.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# TrustedHost 中间件（防止 Host 头攻击）
from starlette.middleware.trustedhost import TrustedHostMiddleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["example.com"])
```

---

## 第十一章 CORS 跨域资源共享

### 11.1 什么是 CORS？

当**前端**和**后端**运行在不同的地址（端口不同、域名不同）时，浏览器出于安全考虑会阻止跨域请求。CORS 就是告诉浏览器"我允许这个前端来访问我"。

**什么算不同的源？**
- `http://localhost:8080`（前端）→ `http://localhost:8000`（后端）：**不同源**（端口不同）
- `http://localhost` → `https://localhost`：**不同源**（协议不同）
- `http://example.com` → `http://api.example.com`：**不同源**（域名不同）

### 11.2 配置 CORS

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 允许的前端地址列表
origins = [
    "http://localhost:8080",
    "http://localhost:3000",
    "https://myapp.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # 允许的源列表
    allow_credentials=True,     # 是否允许携带 Cookie
    allow_methods=["*"],        # 允许的 HTTP 方法（* 表示全部）
    allow_headers=["*"],        # 允许的请求头（* 表示全部）
)
```

**参数详解：**

| 参数 | 说明 | 建议 |
|------|------|------|
| `allow_origins` | 允许访问的前端地址列表 | 生产环境不要用 `["*"]` |
| `allow_credentials` | 是否允许携带 Cookie/认证头 | 需要认证时必须设为 `True` |
| `allow_methods` | 允许的 HTTP 方法 | `["*"]` 或指定 `["GET", "POST"]` |
| `allow_headers` | 允许的请求头 | `["*"]` 或指定具体头名 |
| `max_age` | 浏览器缓存 CORS 预检结果的时间（秒） | 默认 600 |

> 💡 **掘金头条项目的 CORS 配置：**
> ```python
> # main.py
> app.add_middleware(
>     CORSMiddleware,
>     allow_origins=["*"],      # 开发阶段允许所有源
>     allow_credentials=True,   # 允许携带 Cookie（Token）
>     allow_methods=["*"],      # 允许所有 HTTP 方法
>     allow_headers=["*"],      # 允许所有请求头
> )
> ```
> ⚠️ 注意：生产环境中 `allow_origins=["*"]` 不安全，应该改为具体的前端地址。

### 11.3 CORS 工作流程

```
浏览器                         服务器
  │                              │
  │  ① OPTIONS 预检请求           │
  │  "我要从 localhost:8080       │
  │   发 POST 请求，可以吗？"     │
  │ ───────────────────────────→ │
  │                              │
  │  ② 服务器响应 CORS 头          │
  │  "允许 localhost:8080 访问"   │
  │ ←─────────────────────────── │
  │                              │
  │  ③ 发送真正的请求              │
  │ ───────────────────────────→ │
  │                              │
  │  ④ 返回响应                   │
  │ ←─────────────────────────── │
```

---

## 第十二章 异常处理（Exception Handling）

### 12.1 HTTPException

`HTTPException` 是 FastAPI 内置的异常类，用于**主动返回错误响应**：

```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    item = get_item_from_db(item_id)
    if not item:
        # 抛出 HTTPException，FastAPI 自动返回 JSON 错误响应
        raise HTTPException(
            status_code=404,       # HTTP 状态码
            detail="Item not found" # 错误描述
        )
    return item
```

**常见的 HTTP 状态码：**

| 状态码 | 含义 | 使用场景 |
|--------|------|---------|
| 200 | OK | 请求成功 |
| 201 | Created | 创建成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证（Token 无效/过期） |
| 403 | Forbidden | 无权限 |
| 404 | Not Found | 资源不存在 |
| 422 | Unprocessable Entity | 数据验证失败（FastAPI 自动返回） |
| 500 | Internal Server Error | 服务器内部错误 |

### 12.2 使用 starlette.status 常量

```python
from starlette import status

# 使用常量比直接写数字更清晰、不容易出错
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="参数错误")
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录")
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="不存在")
raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="服务器错误")
```

### 12.3 全局异常处理器

在实际项目中，我们希望**统一错误响应格式**。FastAPI 提供了 `add_exception_handler()` 来注册全局异常处理器：

```python
# utils/exception.py
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

async def http_exception_handler(request: Request, exc: HTTPException):
    """处理 HTTP 业务异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None
        }
    )

async def integrity_error_handler(request: Request, exc: IntegrityError):
    """处理数据库完整性约束错误（如唯一键冲突）"""
    error_msg = str(exc.orig)
    if "Duplicate entry" in error_msg:
        detail = "数据已存在"
    else:
        detail = "数据约束冲突"
    return JSONResponse(
        status_code=400,
        content={"code": 400, "message": detail, "data": None}
    )

async def general_exception_handler(request: Request, exc: Exception):
    """兜底：处理所有未捕获的异常"""
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误", "data": None}
    )
```

```python
# utils/exception_handlers.py
def register_exception_handlers(app):
    """注册全局异常处理器——子类在前，父类在后"""
    app.add_exception_handler(HTTPException, http_exception_handler)      # 业务异常
    app.add_exception_handler(IntegrityError, integrity_error_handler)    # 数据库约束
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)  # 数据库通用
    app.add_exception_handler(Exception, general_exception_handler)       # 兜底
```

```python
# main.py
from utils.exception_handlers import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)  # 注册异常处理器
```

**注册顺序原则：越具体的异常越靠前，越通用的越靠后。**

> 💡 **掘金头条项目**的异常处理体系：
> - `HTTPException` → 业务逻辑主动抛出的错误（如用户不存在、Token 过期）
> - `IntegrityError` → 数据库约束错误（如用户名重复）
> - `SQLAlchemyError` → 数据库通用错误
> - `Exception` → 兜底处理所有其他异常

---

## 第十三章 后台任务（Background Tasks）

### 13.1 什么是后台任务？

后台任务是**在响应返回给客户端之后**才执行的操作。适用于不需要用户等待的场景：

- 发送邮件通知
- 生成报表
- 写入日志

### 13.2 基础用法

```python
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()

# 定义后台任务函数
def send_email(email: str, message: str):
    # 模拟发送邮件（实际项目中调用 SMTP）
    print(f"正在发送邮件给 {email}: {message}")

@app.post("/register")
async def register(background_tasks: BackgroundTasks):
    # 注册逻辑...

    # 添加后台任务（不会阻塞响应）
    background_tasks.add_task(send_email, "user@example.com", "欢迎注册！")

    # 响应立即返回，邮件在后台发送
    return {"message": "注册成功"}
```

**`add_task()` 的参数：**
- 第一个参数：要执行的函数
- 后续参数：按顺序传给函数的位置参数
- 关键字参数：`add_task(func, arg1, kwarg1=value)`

### 13.3 后台任务的注意事项

```python
# ❌ 错误示范：把路由里的 db session 传给后台任务
async def wrong_task(db: AsyncSession, user_id: int):
    """
    为什么错？
    - 后台任务在「响应发回前端之后」才执行
    - 此时 get_db 的 finally 已经执行，session 已关闭
    - 再操作 db 会报错
    """
    db.add(something)
    await db.commit()

# ✅ 正确示范：后台任务自己创建 session
async def right_task(user_id: int, email: str):
    """后台任务完全独立，不依赖路由的 db"""
    print(f"正在给 {email} 发送欢迎邮件...")
    async with AsyncSessionLocal() as db:   # 自己创建 session
        log = {"user_id": user_id, "type": "welcome"}
        db.add(log)
        await db.commit()                   # 自己提交
    # async with 结束自动关闭
```

> 💡 **掘金头条项目**中对此有详细说明（routers/users.py 的伪代码区），这是一个非常重要的实践。

---

## 第十四章 JSON 编码工具 jsonable_encoder

### 14.1 为什么需要 jsonable_encoder？

在 Python 中，很多对象不能直接转为 JSON（比如 ORM 对象、datetime 对象、set 等）。`jsonable_encoder` 可以把这些对象转换为 JSON 兼容的字典。

```python
from fastapi.encoders import jsonable_encoder
from datetime import datetime

class FakeDB:
    def __init__(self, title, timestamp):
        self.title = title
        self.timestamp = timestamp

db_item = FakeDB("新闻标题", datetime.now())

# 直接 json.dumps(db_item) 会报错！
# 使用 jsonable_encoder 转换
json_compatible = jsonable_encoder(db_item)
# → {"title": "新闻标题", "timestamp": "2024-01-01T12:00:00"}
```

### 14.2 实际应用场景

> 💡 **掘金头条项目案例**——统一响应封装：
> ```python
> # utils/response.py
> def success_response(message: str = "success", data=None):
>     content = {
>         "code": 200,
>         "message": message,
>         "data": data    # data 可能是 ORM 对象、Pydantic 模型、列表等
>     }
>     # jsonable_encoder 确保所有对象都能正确转为 JSON
>     return JSONResponse(content=jsonable_encoder(content))
> ```

---

## 第十五章 Header 参数与自定义响应

### 15.1 读取请求头（Header）参数

```python
from fastapi import Header

@app.get("/items")
async def read_items(
    user_agent: str | None = Header(None),       # 读取 User-Agent 请求头
    authorization: str = Header(..., alias="Authorization")  # 读取 Authorization
):
    return {"user_agent": user_agent}
```

**注意：** Header 参数名会自动把 `_` 转换为 `-`，即 `user_agent` 对应 `User-Agent` 头。

> 💡 **掘金头条项目案例**——认证依赖中读取 Token：
> ```python
> # utils/auth.py
> async def get_current_user(
>         authorization: str = Header(..., alias="Authorization"),
>         db: AsyncSession = Depends(get_db)
> ):
>     # Authorization 头的值格式："Bearer <token>"
>     token = authorization.replace("Bearer ", "")
>     user = await users.get_user_by_token(db, token)
>     if not user:
>         raise HTTPException(status_code=401, detail="无效的令牌")
>     return user
> ```

### 15.2 JSONResponse 自定义响应

```python
from fastapi.responses import JSONResponse

@app.get("/items")
async def read_items():
    # 手动构造 JSON 响应，可以设置状态码和自定义头
    return JSONResponse(
        status_code=200,
        content={"code": 200, "message": "success", "data": []},
        headers={"X-Custom-Header": "value"}
    )
```

### 15.3 其他响应类型

```python
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, StreamingResponse

# HTML 响应
@app.get("/html", response_class=HTMLResponse)
async def get_html():
    return "<h1>Hello</h1>"

# 重定向
@app.get("/old-page")
async def old_page():
    return RedirectResponse(url="/new-page")

# 文件下载
@app.get("/download")
async def download():
    return FileResponse("file.pdf", filename="report.pdf")
```

---

## 第十六章 生命周期事件（Lifespan Events）

### 16.1 应用启动和关闭时执行代码

使用 `lifespan` 上下文管理器在应用启动和关闭时执行操作：

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---- 应用启动时执行 ----
    print("应用启动中...")
    # 比如：初始化数据库连接池、加载缓存数据
    yield
    # ---- 应用关闭时执行 ----
    print("应用正在关闭...")
    # 比如：关闭数据库连接、清理资源

app = FastAPI(lifespan=lifespan)
```

### 16.2 典型使用场景

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时：创建数据库表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 启动时：初始化 Redis 连接
    await redis_client.ping()

    yield  # 应用运行中...

    # 关闭时：清理资源
    await redis_client.close()
    await engine.dispose()
```

---

## 第十七章 项目架构与最佳实践

### 17.1 推荐的项目结构

```
project/
├── main.py              # 应用入口，创建 FastAPI 实例、注册路由和中间件
├── config/              # 配置文件
│   ├── db_conf.py       #   数据库配置（连接池、session 工厂）
│   └── cache_conf.py    #   缓存配置（Redis 连接）
├── models/              # SQLAlchemy ORM 模型（对应数据库表）
│   ├── news.py
│   ├── users.py
│   ├── favorite.py
│   └── history.py
├── schemas/             # Pydantic 模型（请求/响应数据验证）
│   ├── base.py          #   公共基础模型
│   ├── news.py
│   ├── users.py
│   ├── favorite.py
│   └── history.py
├── routers/             # 路由层（定义 API 接口、调用 crud）
│   ├── news.py
│   ├── users.py
│   ├── favorite.py
│   └── history.py
├── crud/                # 数据库操作层（封装所有 SQL 操作）
│   ├── news.py
│   ├── users.py
│   ├── favorite.py
│   └── history.py
├── cache/               # 缓存操作层
│   └── news_cache.py
├── utils/               # 工具函数
│   ├── auth.py          #   认证相关（Token 验证、依赖注入）
│   ├── security.py      #   密码加密
│   ├── jwt_util.py      #   JWT 工具
│   ├── response.py      #   统一响应格式
│   ├── exception.py     #   异常处理函数
│   └── exception_handlers.py  # 注册异常处理器
├── requirements.txt     # Python 依赖
└── .gitignore
```

### 17.2 各层的职责

```
┌─────────────────────────────────────────────┐
│  routers（路由层）                            │
│  定义 API 接口、参数验证、调用 crud           │
├─────────────────────────────────────────────┤
│  crud（数据访问层）                           │
│  封装所有数据库操作（增删改查）                │
├─────────────────────────────────────────────┤
│  models（模型层）                             │
│  SQLAlchemy ORM 模型，定义数据库表结构         │
├─────────────────────────────────────────────┤
│  schemas（数据验证层）                         │
│  Pydantic 模型，定义请求/响应的数据格式         │
├─────────────────────────────────────────────┤
│  config（配置层）                             │
│  数据库连接、Redis 连接等配置                  │
├─────────────────────────────────────────────┤
│  utils（工具层）                              │
│  认证、加密、响应封装、异常处理等公共工具         │
└─────────────────────────────────────────────┘
```

### 17.3 一个完整请求的数据流

以「获取新闻列表」为例：

```
客户端请求
  GET /api/news/list?categoryId=1&page=1&pageSize=10
       │
       ▼
  ┌──────────┐    中间件处理（CORS 等）
  │   main    │
  └────┬─────┘
       │
       ▼
  ┌─────────────────────────────────────┐
  │  routers/news.py                    │
  │  1. FastAPI 执行 Depends(get_db)    │  ← 依赖注入：创建数据库 session
  │  2. 解析查询参数 categoryId=1, page=1│
  │  3. 调用 news_cache.get_news_list() │
  └────────┬────────────────────────────┘
           │
           ▼
  ┌─────────────────────────────────────┐
  │  crud/news_cache.py                 │
  │  1. 先查 Redis 缓存                 │
  │  2. 缓存命中 → 直接返回              │
  │  3. 缓存未命中 → 查数据库            │
  └────────┬────────────────────────────┘
           │
           ▼
  ┌─────────────────────────────────────┐
  │  models/news.py (News 表)           │
  │  SQLAlchemy 执行 SELECT 查询        │
  └────────┬────────────────────────────┘
           │
           ▼
  ┌─────────────────────────────────────┐
  │  routers/news.py                    │
  │  1. 组装响应数据 NewsListResponse    │
  │  2. 调用 success_response() 返回    │
  └────────┬────────────────────────────┘
           │
           ▼
  ┌─────────────────────────────────────┐
  │  utils/response.py                  │
  │  jsonable_encoder 转换 → JSONResponse│
  └────────┬────────────────────────────┘
           │
           ▼
  ┌─────────────────────────────────────┐
  │  get_db() 的 yield 之后              │
  │  session.commit() → session.close() │
  └─────────────────────────────────────┘
           │
           ▼
  响应返回给客户端
  {"code": 200, "message": "获取新闻列表成功", "data": {...}}
```

### 17.4 关键编程模式总结

#### 模式 1：统一响应格式
```python
# 所有接口都返回统一格式
return success_response(message="操作成功", data=数据)
# → {"code": 200, "message": "操作成功", "data": {...}}
```

#### 模式 2：ORM → Pydantic → JSON 的转换链
```python
# 数据库 ORM 对象 → Pydantic 模型 → 字典 → JSON 响应
pydantic_obj = MyResponse.model_validate(orm_obj)     # ORM → Pydantic
data_dict = pydantic_obj.model_dump(by_alias=True)    # Pydantic → 字典
return success_response(data=data_dict)                # 字典 → JSON
```

#### 模式 3：缓存优先策略
```python
# 1. 先查缓存
cached = await get_cache(key)
if cached:
    return cached

# 2. 缓存未命中，查数据库
data = await db_query(...)

# 3. 写入缓存
await set_cache(key, data, expire=3600)
return data
```

#### 模式 4：认证保护的接口
```python
@router.get("/protected")
async def protected_route(
    user: User = Depends(get_current_user),    # 必须登录
    db: AsyncSession = Depends(get_db)          # 数据库连接
):
    # user 就是当前登录的用户
    ...
```

---

## 附录 A：FastAPI 常用导入速查表

```python
# ---- 核心 ----
from fastapi import FastAPI, APIRouter
from fastapi import Depends, Query, Path, Header, Body, Cookie
from fastapi import HTTPException, Request
from fastapi import BackgroundTasks

# ---- 响应 ----
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse, FileResponse
from fastapi.encoders import jsonable_encoder

# ---- 中间件 ----
from fastapi.middleware.cors import CORSMiddleware

# ---- Pydantic ----
from pydantic import BaseModel, Field, ConfigDict, validator

# ---- SQLAlchemy 异步 ----
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# ---- 状态码常量 ----
from starlette import status
```

## 附录 B：HTTP 状态码速查表

| 类别 | 状态码 | 含义 |
|------|--------|------|
| **成功** | 200 | OK - 请求成功 |
| | 201 | Created - 创建成功 |
| | 204 | No Content - 成功但无返回内容 |
| **客户端错误** | 400 | Bad Request - 请求参数错误 |
| | 401 | Unauthorized - 未认证 |
| | 403 | Forbidden - 无权限 |
| | 404 | Not Found - 资源不存在 |
| | 409 | Conflict - 资源冲突 |
| | 422 | Unprocessable Entity - 数据验证失败 |
| **服务器错误** | 500 | Internal Server Error - 服务器内部错误 |
| | 502 | Bad Gateway - 网关错误 |
| | 503 | Service Unavailable - 服务不可用 |

## 附录 C：掘金头条项目 API 接口一览表

| 模块 | 方法 | 路径 | 说明 | 需要认证 |
|------|------|------|------|---------|
| 新闻 | GET | /api/news/categories | 获取新闻分类 | 否 |
| 新闻 | GET | /api/news/list | 获取新闻列表 | 否 |
| 新闻 | GET | /api/news/detail | 获取新闻详情 | 否 |
| 用户 | POST | /api/user/register | 用户注册 | 否 |
| 用户 | POST | /api/user/login | 用户登录 | 否 |
| 用户 | GET | /api/user/info | 获取用户信息 | 是 |
| 用户 | PUT | /api/user/update | 修改用户信息 | 是 |
| 用户 | PUT | /api/user/password | 修改密码 | 是 |
| 收藏 | GET | /api/favorite/check | 检查收藏状态 | 是 |
| 收藏 | POST | /api/favorite/add | 添加收藏 | 是 |
| 收藏 | DELETE | /api/favorite/remove | 取消收藏 | 是 |
| 收藏 | GET | /api/favorite/list | 获取收藏列表 | 是 |
| 收藏 | DELETE | /api/favorite/clear | 清空收藏 | 是 |
| 历史 | POST | /api/history/add | 添加历史记录 | 是 |
| 历史 | GET | /api/history/list | 获取历史列表 | 是 |
| 历史 | DELETE | /api/history/delete/{history_id} | 删除历史记录 | 是 |
| 历史 | DELETE | /api/history/clear | 清空历史记录 | 是 |
