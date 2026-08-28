# Pydantic v2 完全学习手册

> 本手册基于 Pydantic v2 官方文档整理，结合「掘金头条」后端项目（toutiao_backend）的实际代码作为案例。
> 适合零基础小白从头学起。Pydantic 是 FastAPI 的"数据验证引擎"，学好 Pydantic 是掌握 FastAPI 的关键。

---

## 目录

- [第一章 Pydantic 简介与安装](#第一章-pydantic-简介与安装)
- [第二章 BaseModel 基础](#第二章-basemodel-基础)
- [第三章 字段类型详解](#第三章-字段类型详解)
- [第四章 Field() 函数详解](#第四章-field-函数详解)
- [第五章 model_config 配置](#第五章-model_config-配置)
- [第六章 字段别名（alias）](#第六章-字段别名alias)
- [第七章 模型继承与组合](#第七章-模型继承与组合)
- [第八章 数据验证（Validators）](#第八章-数据验证validators)
- [第九章 序列化与反序列化](#第九章-序列化与反序列化)
- [第十章 model_validate 与 model_dump](#第十章-model_validate-与-model_dump)
- [第十一章 嵌套模型与复杂类型](#第十一章-嵌套模型与复杂类型)
- [第十二章 在 FastAPI 中的使用模式](#第十二章-在-fastapi-中的使用模式)
- [第十三章 常见错误与调试](#第十三章-常见错误与调试)
- [第十四章 项目实战总结](#第十四章-项目实战总结)

---

## 第一章 Pydantic 简介与安装

### 1.1 什么是 Pydantic？

Pydantic 是 Python 的**数据验证库**。它的核心能力：

| 能力 | 说明 |
|------|------|
| **数据验证** | 自动检查数据是否符合定义的类型和规则 |
| **类型转换** | 自动将输入数据转换为正确的 Python 类型 |
| **序列化** | 将 Python 对象转换为 JSON 兼容的字典 |
| **反序列化** | 将字典/JSON 转换为 Python 对象 |
| **文档生成** | 自动生成 JSON Schema，供 FastAPI 生成 API 文档 |

**一句话总结：** Pydantic 就是你数据的"质检员"——定义好规则，Pydantic 帮你自动检查和转换。

### 1.2 为什么 FastAPI 离不开 Pydantic？

```
客户端请求 → Pydantic 验证请求数据 → 业务逻辑处理 → Pydantic 序列化响应数据 → 返回客户端
```

FastAPI 在三个地方使用 Pydantic：
1. **请求体**：定义前端发送数据的格式
2. **响应体**：定义返回给前端数据的格式
3. **API 文档**：基于 Pydantic 模型自动生成 Swagger UI 文档

### 1.3 安装

```bash
pip install pydantic
# FastAPI 项目中已经包含，不需要单独安装
```

> 💡 **掘金头条项目** 使用 Pydantic 2.12.5。

### 1.4 Pydantic v1 vs v2 的关键变化

| 特性 | v1 | v2（推荐） |
|------|-----|-----------|
| 配置方式 | `class Config:` | `model_config = ConfigDict(...)` |
| ORM 模式 | `orm_mode = True` | `from_attributes = True` |
| 验证方法 | `.from_orm(obj)` | `.model_validate(obj)` |
| 序列化方法 | `.dict()` | `.model_dump()` |
| JSON 序列化 | `.json()` | `.model_dump_json()` |
| 字段排除 | `.dict(exclude={"field"})` | `.model_dump(exclude={"field"})` |

---

## 第二章 BaseModel 基础

### 2.1 定义第一个模型

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str          # 必填字符串
    age: int           # 必填整数
    email: str         # 必填字符串
```

就这么简单！你已经定义了一个数据模型，Pydantic 会自动验证数据。

### 2.2 创建实例

```python
# 正常创建
user = User(name="张三", age=25, email="zhang@example.com")
print(user.name)    # → "张三"
print(user.age)     # → 25

# 自动类型转换
user = User(name="张三", age="25", email="zhang@example.com")
# age 是字符串 "25"，Pydantic 自动转为整数 25

# 数据验证失败
user = User(name="张三", age="not_a_number", email="zhang@example.com")
# → ValidationError: age - Input should be a valid integer
```

### 2.3 必填 vs 可选字段

```python
from typing import Optional

class User(BaseModel):
    name: str                       # 必填（没有默认值）
    age: int                        # 必填（没有默认值）
    nickname: Optional[str] = None  # 可选（有默认值 None）
    bio: str = "这个人很懒"           # 可选（有默认值）
```

**规则很简单：**
- **没有默认值** → 必填
- **有默认值**（包括 `None`） → 可选

### 2.4 模型实例的基本操作

```python
user = User(name="张三", age=25, email="zhang@example.com")

# 访问属性
print(user.name)           # "张三"

# 修改属性
user.name = "李四"
print(user.name)           # "李四"

# 比较
user2 = User(name="李四", age=25, email="zhang@example.com")
print(user == user2)       # True（相同数据 = 相等）

# 获取所有字段
print(user.model_fields)   # 返回所有字段的元信息
```

---

## 第三章 字段类型详解

### 3.1 基础类型

```python
from pydantic import BaseModel

class Example(BaseModel):
    # 基础类型
    name: str            # 字符串
    age: int             # 整数
    score: float         # 浮点数
    is_active: bool      # 布尔值
    # Pydantic 的类型转换能力：
    # "123" → 123 (str → int)
    # "3.14" → 3.14 (str → float)
    # "true" → True, "1" → True, "yes" → True (str → bool)
    # 1 → True, 0 → False (int → bool)
```

### 3.2 可选类型

```python
from typing import Optional

class User(BaseModel):
    # Python 3.10+ 语法
    nickname: str | None = None        # 可以是 str 或 None
    # 等价于：
    nickname: Optional[str] = None     # 老语法，效果相同
```

### 3.3 列表类型

```python
class NewsList(BaseModel):
    # 列表
    titles: list[str]                          # 字符串列表
    scores: list[int]                          # 整数列表
    items: list[dict]                          # 字典列表

    # 带默认值
    tags: list[str] = []                       # 空列表
    # ⚠️ 注意：不能用 list[str] = [] 作为默认值（可变默认值陷阱）
    # ✅ 正确做法：使用 default_factory（详见 Field 章节）
    tags: list[str] = Field(default_factory=list)
```

### 3.4 字典类型

```python
class Config(BaseModel):
    settings: dict[str, str]                   # 键和值都是字符串
    metadata: dict[str, int]                   # 键是字符串，值是整数
    extra: dict = {}                           # 不限制类型
```

### 3.5 日期时间类型

```python
from datetime import datetime, date, time

class Event(BaseModel):
    created_at: datetime     # 日期时间：2024-01-01T12:00:00
    birthday: date           # 日期：2024-01-01
    alarm: time              # 时间：12:00:00
    # Pydantic 会自动解析字符串为 datetime 对象
    # "2024-01-01 12:00:00" → datetime(2024, 1, 1, 12, 0, 0)
```

### 3.6 枚举类型

```python
from enum import Enum

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"

class User(BaseModel):
    gender: Gender = Gender.UNKNOWN
    # 只允许 "male"、"female"、"unknown" 三个值
```

### 3.7 Union 联合类型

```python
from typing import Union

class Response(BaseModel):
    # data 可以是字符串或整数
    data: Union[str, int]
    # Python 3.10+ 语法
    data: str | int
```

> 💡 **掘金头条项目案例**——基础模型中使用了多种类型：
> ```python
> # schemas/base.py
> class NewsItemBase(BaseModel):
>     id: int                                    # 整数
>     title: str                                 # 字符串
>     description: Optional[str] = None          # 可选字符串
>     image: Optional[str] = None                # 可选字符串
>     author: Optional[str] = None               # 可选字符串
>     category_id: int = Field(alias="categoryId")  # 整数 + 别名
>     views: int                                 # 整数
>     publish_time: Optional[datetime] = Field(None, alias="publishTime")  # 可选日期时间
> ```

---

## 第四章 Field() 函数详解

### 4.1 Field() 是什么？

`Field()` 是 Pydantic 提供的函数，用于给字段添加**额外的验证规则**和**元数据信息**。它是字段的"增强器"。

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(
        ...,                    # 第一个参数：默认值（... 表示必填）
        min_length=1,           # 最小长度
        max_length=100,         # 最大长度
        description="商品名称"   # 描述（用于 API 文档）
    )
```

### 4.2 默认值与必填

```python
from pydantic import Field

class User(BaseModel):
    # 必填字段（... 表示必填，没有默认值）
    username: str = Field(...)
    
    # 有默认值
    age: int = Field(18)
    
    # 可选字段（默认值为 None）
    nickname: str = Field(None)
    
    # 简写方式（不用 Field）
    bio: str = "默认简介"           # 等价于 Field("默认简介")
    username: str                   # 等价于 Field(...)
```

### 4.3 字符串约束

```python
class User(BaseModel):
    username: str = Field(
        ...,
        min_length=3,            # 最小长度
        max_length=50,           # 最大长度
        pattern=r"^[a-zA-Z0-9_]+$"  # 正则表达式（只允许字母、数字、下划线）
    )
    password: str = Field(..., min_length=6, max_length=128)
    nickname: str = Field(None, max_length=50, description="昵称")
```

### 4.4 数值约束

```python
class Product(BaseModel):
    price: float = Field(
        ...,
        gt=0,                # 大于 0（> 0）
        le=99999             # 小于等于 99999（<= 99999）
    )
    quantity: int = Field(0, ge=0)   # 大于等于 0（>= 0）
    rating: float = Field(0, ge=0, le=5)  # 0~5 之间
```

**数值约束参数速查：**

| 参数 | 含义 | 数学表示 |
|------|------|---------|
| `gt` | 大于 | `> x` |
| `ge` | 大于等于 | `>= x` |
| `lt` | 小于 | `< x` |
| `le` | 小于等于 | `<= x` |
| `multiple_of` | 是...的倍数 | `x % n == 0` |

### 4.5 description 描述

```python
class User(BaseModel):
    old_password: str = Field(..., alias="oldPassword", description="旧密码")
    new_password: str = Field(..., min_length=6, alias="newPassword", description="新密码")
```

`description` 会被 FastAPI 展示在 Swagger UI 文档中，帮助用户理解每个字段的含义。

### 4.6 default_factory 动态默认值

```python
from pydantic import Field, BaseModel
from datetime import datetime

class Log(BaseModel):
    # ❌ 错误：可变默认值（所有实例共享同一个列表）
    items: list = []

    # ✅ 正确：每次创建实例时调用工厂函数
    items: list = Field(default_factory=list)

    # ✅ 动态默认值
    created_at: datetime = Field(default_factory=datetime.now)
    related_news: list = Field(default_factory=list)
```

> 💡 **掘金头条项目案例**——`default_factory` 的使用：
> ```python
> # schemas/news.py
> class NewsDetailResponse(NewsItemBase):
>     content: str
>     related_news: list[RelatedNewsResponse] = Field(
>         default_factory=list,      # 默认空列表
>         alias="relatedNews"
>     )
> ```

---

## 第五章 model_config 配置

### 5.1 什么是 model_config？

`model_config` 是 Pydantic v2 引入的配置方式，用于控制模型的整体行为。它替代了 v1 中的 `class Config`。

```python
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,    # 允许从 ORM 对象取值
        populate_by_name=True    # 同时支持字段名和别名
    )

    name: str
    age: int
```

### 5.2 核心配置项

#### from_attributes（ORM 模式）

```python
from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    nickname: str | None = None

# 有了 from_attributes=True，可以直接从 ORM 对象创建 Pydantic 模型
user_orm = session.query(User).first()  # SQLAlchemy ORM 对象
user_response = UserResponse.model_validate(user_orm)  # ✅ 自动从 ORM 对象属性取值
```

**没有 `from_attributes=True` 会怎样？**
```python
# model_validate 只能接受字典
user_response = UserResponse.model_validate(user_orm)  # ❌ 报错！
# 因为默认只接受字典，不认识 ORM 对象
```

#### populate_by_name（别名兼容）

```python
from pydantic import BaseModel, ConfigDict, Field

class User(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    category_id: int = Field(alias="categoryId")

# 有了 populate_by_name=True，两种方式都能用：
User(category_id=1)      # ✅ 用字段名
User(categoryId=1)       # ✅ 用别名

# 没有 populate_by_name=True（默认 False）：
User(category_id=1)      # ❌ 报错！只能用别名
User(categoryId=1)       # ✅ 只有这个可以
```

#### str_strip_whitespace（自动去空格）

```python
class User(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    
    name: str

user = User(name="  张三  ")
print(user.name)  # → "张三"（自动去掉了两端空格）
```

#### str_to_lower / str_to_upper

```python
class User(BaseModel):
    model_config = ConfigDict(str_to_lower=True)
    
    email: str

user = User(email="John@Example.COM")
print(user.email)  # → "john@example.com"
```

#### extra（额外字段处理）

```python
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")  # 忽略额外字段
    
    name: str

# extra 的三个选项：
# "ignore" → 忽略额外字段（默认）
# "allow"  → 允许额外字段（存入模型）
# "forbid" → 禁止额外字段（报错）

user = User(name="张三", age=25)
# extra="ignore" → age 被忽略
# extra="allow"  → age 被保留
# extra="forbid" → 报错
```

### 5.3 所有常用配置项速查

| 配置项 | 类型 | 说明 |
|--------|------|------|
| `from_attributes` | bool | 允许从对象属性取值（ORM 兼容） |
| `populate_by_name` | bool | 同时支持字段名和别名 |
| `str_strip_whitespace` | bool | 自动去除字符串两端空格 |
| `str_to_lower` | bool | 自动转小写 |
| `str_to_upper` | bool | 自动转大写 |
| `extra` | str | 额外字段处理："ignore"/"allow"/"forbid" |
| `frozen` | bool | 不可变模型（所有字段只读） |
| `validate_assignment` | bool | 赋值时也进行验证 |
| `str_max_length` | int | 所有字符串字段的最大长度 |
| `str_min_length` | int | 所有字符串字段的最小长度 |

> 💡 **掘金头条项目案例**——最常见的配置组合：
> ```python
> model_config = ConfigDict(
>     from_attributes=True,     # 从 ORM 对象取值
>     populate_by_name=True     # 字段名和别名都支持
> )
> ```
> 这个组合在项目的 `schemas/` 目录下几乎每个响应模型中都在使用。

---

## 第六章 字段别名（alias）

### 6.1 为什么需要别名？

前后端命名规范经常不一致：

| 角色 | 命名风格 | 示例 |
|------|----------|------|
| **前端（JavaScript）** | 驼峰命名 `camelCase` | `categoryId`、`publishTime` |
| **后端（Python）** | 蛇形命名 `snake_case` | `category_id`、`publish_time` |
| **数据库** | 蛇形命名 `snake_case` | `category_id`、`publish_time` |

别名就是做**字段名的翻译**——Python 代码里用蛇形，JSON 数据里用驼峰。

### 6.2 定义别名

```python
from pydantic import BaseModel, Field

class News(BaseModel):
    # Python 里用 category_id，JSON 里用 categoryId
    category_id: int = Field(alias="categoryId")
    publish_time: str = Field(None, alias="publishTime")
    is_top: bool = Field(False, alias="isTop")
```

### 6.3 别名 vs 字段名

```python
news = News(categoryId=1)       # ✅ 使用别名创建
news = News(category_id=1)      # ❌ 默认不支持字段名

# 除非配置了 populate_by_name=True
class News(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    category_id: int = Field(alias="categoryId")

news = News(category_id=1)      # ✅ 字段名也可以了
news = News(categoryId=1)       # ✅ 别名也可以
```

### 6.4 序列化时的别名

```python
news = News(categoryId=1, publishTime="2024-01-01")

# model_dump() 默认使用字段名
print(news.model_dump())
# → {"category_id": 1, "publish_time": "2024-01-01"}

# model_dump(by_alias=True) 使用别名
print(news.model_dump(by_alias=True))
# → {"categoryId": 1, "publishTime": "2024-01-01"}
```

### 6.5 别名在 FastAPI 中的使用场景

```python
# 请求体（前端发送 JSON，用驼峰命名）
class FavoriteAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")
# 前端发送: {"newsId": 123}
# Pydantic 自动映射到 Python 的 news_id

# 查询参数（前端传 URL 参数，用驼峰命名）
@router.get("/list")
async def get_list(
    category_id: int = Query(..., alias="categoryId"),
    page_size: int = Query(10, alias="pageSize")
):
    # Python 里使用 category_id、page_size
    # 前端传 ?categoryId=1&pageSize=10
```

> 💡 **掘金头条项目案例**——项目中大量使用别名：
> ```python
> # schemas/base.py
> class NewsItemBase(BaseModel):
>     category_id: int = Field(alias="categoryId")
>     publish_time: Optional[datetime] = Field(None, alias="publishTime")
>     model_config = ConfigDict(from_attributes=True, populate_by_name=True)
>
> # schemas/favorite.py
> class FavoriteAddRequest(BaseModel):
>     news_id: int = Field(..., alias="newsId")
>
> # schemas/history.py
> class HistoryNewsItemResponse(NewsItemBase):
>     history_id: int = Field(alias="historyId")
>     view_time: datetime = Field(alias="viewTime")
> ```

---

## 第七章 模型继承与组合

### 7.1 基础继承

Pydantic 模型支持 Python 的类继承，子类自动拥有父类的所有字段：

```python
class BaseUser(BaseModel):
    id: int
    username: str

class DetailedUser(BaseUser):          # 继承 BaseUser
    email: str                          # 新增字段
    phone: str | None = None            # 新增可选字段

user = DetailedUser(id=1, username="zhangsan", email="zhang@example.com")
# user.id = 1          ← 来自父类
# user.username = "zhangsan" ← 来自父类
# user.email = "zhang@example.com" ← 子类新增
```

### 7.2 覆盖父类字段

```python
class BaseUser(BaseModel):
    name: str
    bio: str = "默认简介"

class VipUser(BaseUser):
    # 覆盖父类字段，添加更多约束
    name: str = Field(..., min_length=2, max_length=50)
    bio: str = Field("VIP 用户", max_length=500)
    level: int = Field(1, ge=1, le=10)  # 新增字段
```

### 7.3 实际项目中的继承模式

> 💡 **掘金头条项目案例**——经典的"基础模型 + 扩展模型"模式：
>
> **第一步**：定义公共基础模型
> ```python
> # schemas/base.py
> class NewsItemBase(BaseModel):
>     id: int
>     title: str
>     description: Optional[str] = None
>     image: Optional[str] = None
>     author: Optional[str] = None
>     category_id: int = Field(alias="categoryId")
>     views: int
>     publish_time: Optional[datetime] = Field(None, alias="publishTime")
>
>     model_config = ConfigDict(from_attributes=True, populate_by_name=True)
> ```
>
> **第二步**：基于基础模型扩展
> ```python
> # schemas/news.py — 新闻详情（继承基础 + 新增字段）
> class NewsDetailResponse(NewsItemBase):
>     content: str                                                    # 新增：新闻内容
>     related_news: list[RelatedNewsResponse] = Field(
>         default_factory=list, alias="relatedNews"
>     )                                                               # 新增：相关新闻
>
> # schemas/favorite.py — 收藏新闻（继承基础 + 新增字段）
> class FavoriteNewsItemResponse(NewsItemBase):
>     favorite_id: int = Field(alias="favoriteId")                    # 新增：收藏 ID
>     favorite_time: datetime = Field(alias="favoriteTime")           # 新增：收藏时间
>
> # schemas/history.py — 历史新闻（继承基础 + 新增字段）
> class HistoryNewsItemResponse(NewsItemBase):
>     history_id: int = Field(alias="historyId")                      # 新增：历史 ID
>     view_time: datetime = Field(alias="viewTime")                   # 新增：浏览时间
> ```
>
> **继承关系图：**
> ```
> NewsItemBase (基础新闻)
> ├── NewsDetailResponse (+content, +related_news)
> ├── FavoriteNewsItemResponse (+favorite_id, +favorite_time)
> └── HistoryNewsItemResponse (+history_id, +view_time)
> ```

### 7.4 模型组合（嵌套模型）

一个模型的字段可以是另一个模型的类型：

```python
class Address(BaseModel):
    city: str
    street: str

class User(BaseModel):
    name: str
    address: Address        # 嵌套 Address 模型

# 创建时传入字典，Pydantic 自动转换为 Address 对象
user = User(
    name="张三",
    address={"city": "北京", "street": "长安街"}
)
print(user.address.city)   # → "北京"
```

> 💡 **掘金头条项目案例**——嵌套模型：
> ```python
> # schemas/users.py
> class UserAuthResponse(BaseModel):
>     token: str
>     user_info: UserInfoResponse = Field(..., alias="userInfo")
>     # user_info 的类型是 UserInfoResponse，这是一个嵌套模型
> ```

---

## 第八章 数据验证（Validators）

### 8.1 为什么需要自定义验证？

Field() 的内置约束（min_length、gt 等）覆盖了常见场景，但有时你需要更复杂的验证逻辑：

- 验证邮箱格式
- 验证密码强度
- 字段之间的交叉验证
- 自定义错误消息

### 8.2 field_validator（字段级验证器）

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    username: str
    email: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        # v 是字段的值
        if len(v) < 3:
            raise ValueError("用户名至少 3 个字符")
        if " " in v:
            raise ValueError("用户名不能包含空格")
        return v   # 返回处理后的值

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("邮箱格式不正确")
        return v.lower()   # 自动转小写
```

**关键点：**
- `@classmethod` 是必须的
- `cls` 是类本身（和普通类方法一样）
- `v` 是字段的值
- 返回的值会替代原始值（可以做数据清洗）
- 抛出 `ValueError` 表示验证失败

### 8.3 model_validator（模型级验证器）

用于**字段之间的交叉验证**——一个字段的有效性取决于另一个字段的值：

```python
from pydantic import BaseModel, model_validator

class ChangePassword(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str

    @model_validator(mode="after")
    def check_passwords_match(self):
        # self 是整个模型实例
        if self.new_password != self.confirm_password:
            raise ValueError("新密码和确认密码不一致")
        if self.new_password == self.old_password:
            raise ValueError("新密码不能和旧密码相同")
        return self
```

**mode 参数：**
- `mode="after"` → 所有字段验证通过后执行（可以访问 self）
- `mode="before"` → 在任何验证之前执行（处理原始输入数据）

### 8.4 验证器执行顺序

```
1. 类型验证（str、int 等）
2. field_validator(mode="before")
3. Field() 约束（min_length、gt 等）
4. field_validator(mode="after")
5. model_validator(mode="before")
6. model_validator(mode="after")
```

### 8.5 验证器的实际应用

虽然掘金头条项目没有使用显式的 validator 装饰器，但 Pydantic 的 Field() 约束本质上就是验证：

```python
# 这些 Field 约束就是隐式验证器
class UserChangePasswordRequest(BaseModel):
    old_password: str = Field(..., alias="oldPassword")
    new_password: str = Field(..., min_length=6, alias="newPassword")
    # min_length=6 → 如果密码少于 6 位，自动返回 422 错误
```

---

## 第九章 序列化与反序列化

### 9.1 概念

| 方向 | 术语 | 说明 |
|------|------|------|
| Python 对象 → JSON/字典 | **序列化** | `model_dump()` / `model_dump_json()` |
| JSON/字典 → Python 对象 | **反序列化** | `model_validate()` / `model_validate_json()` |

```
  序列化
对象 ────→ 字典/JSON
  ↑          ↓
  └──────────┘
  反序列化
```

### 9.2 model_dump()（模型 → 字典）

```python
user = User(id=1, name="张三", category_id=5)

# 基础用法
user.model_dump()
# → {"id": 1, "name": "张三", "category_id": 5}

# 使用别名
user.model_dump(by_alias=True)
# → {"id": 1, "name": "张三", "categoryId": 5}

# 排除某些字段
user.model_dump(exclude={"name"})
# → {"id": 1, "category_id": 5}

# 只包含某些字段
user.model_dump(include={"id", "name"})
# → {"id": 1, "name": "张三"}

# JSON 兼容模式（datetime → 字符串，Decimal → float 等）
user.model_dump(mode="json")
# → 所有值都是 JSON 可序列化类型

# 排除未设置的字段
user.model_dump(exclude_unset=True)
# → 只包含被显式设置过的字段

# 排除 None 值
user.model_dump(exclude_none=True)
# → 不包含值为 None 的字段
```

### 9.3 model_dump_json()（模型 → JSON 字符串）

```python
user = User(id=1, name="张三")
json_str = user.model_dump_json()
# → '{"id": 1, "name": "张三"}'

# 格式化输出（缩进）
json_str = user.model_dump_json(indent=2)
```

### 9.4 model_dump() 的参数详解

| 参数 | 类型 | 说明 |
|------|------|------|
| `by_alias` | bool | 使用别名作为 key（默认 False） |
| `exclude` | set | 排除的字段集合 |
| `include` | set | 包含的字段集合 |
| `mode` | str | "python"（默认）或 "json"（确保 JSON 兼容） |
| `exclude_unset` | bool | 排除未显式设置的字段 |
| `exclude_none` | bool | 排除值为 None 的字段 |
| `exclude_defaults` | bool | 排除值为默认值的字段 |

### 9.5 组合使用的典型场景

```python
# 场景：将 ORM 对象转为 JSON 兼容的字典，存入 Redis 缓存
news_data = NewsItemBase.model_validate(orm_obj).model_dump(
    mode="json",          # 确保 datetime 等类型转为字符串
    by_alias=False        # 用 Python 原始字段名（Redis 数据是给后端用的）
)
# → {"id": 1, "title": "新闻标题", "category_id": 1, "publish_time": "2024-01-01T12:00:00", ...}

# 场景：更新用户时只更新传了的字段
update_data = user_data.model_dump(
    exclude_unset=True,   # 只包含用户实际传了的字段
    exclude_none=True     # 排除 None 值
)
# → {"nickname": "新昵称"}  # 只更新了 nickname，其他字段不变
```

---

## 第十章 model_validate 与 model_dump

### 10.1 model_validate()（其他对象 → 模型）

`model_validate()` 是 Pydantic v2 的核心方法，用于将**其他类型的数据**转换为 Pydantic 模型：

```python
# 从字典创建
user = User.model_validate({"id": 1, "name": "张三"})

# 从 ORM 对象创建（需要 from_attributes=True）
user = UserResponse.model_validate(orm_user_object)
```

### 10.2 model_validate_json()（JSON 字符串 → 模型）

```python
json_str = '{"id": 1, "name": "张三"}'
user = User.model_validate_json(json_str)
```

### 10.3 ORM 对象转换的完整流程

这是在 FastAPI + SQLAlchemy 项目中最常见的模式：

```python
# 第 1 步：从数据库查询得到 ORM 对象
orm_user = await db.get(User, 1)
# orm_user 是 SQLAlchemy 的 User 对象

# 第 2 步：将 ORM 对象转为 Pydantic 模型
user_response = UserInfoResponse.model_validate(orm_user)
# 需要 UserInfoResponse 配置了 from_attributes=True
# Pydantic 会自动读取 orm_user.id, orm_user.username 等属性

# 第 3 步：将 Pydantic 模型转为字典
user_dict = user_response.model_dump()

# 第 4 步：返回 JSON 响应
return success_response(data=user_dict)
```

> 💡 **掘金头条项目案例**——完整的 ORM → Pydantic → 字典 转换链：
> ```python
> # routers/users.py — 注册接口
> user = await users.create_user(db, user_data)        # ORM User 对象
> response_data = UserAuthResponse(
>     token=token,
>     user_info=UserInfoResponse.model_validate(user)   # ORM → Pydantic
> )
> return success_response(message="注册成功", data=response_data)
> # success_response 内部会调用 jsonable_encoder，自动将 Pydantic 对象转为 JSON
> ```

### 10.4 model_validate vs __init__

```python
# 方式一：__init__（用关键字参数）
user = User(id=1, name="张三")

# 方式二：model_validate（用字典或对象）
user = User.model_validate({"id": 1, "name": "张三"})
user = User.model_validate(orm_object)

# 区别：
# __init__ 只能接受关键字参数
# model_validate 可以接受字典、ORM 对象、dataclass 等
# model_validate + from_attributes=True 可以处理 ORM 对象
```

---

## 第十一章 嵌套模型与复杂类型

### 11.1 嵌套模型

```python
class Address(BaseModel):
    city: str
    street: str

class User(BaseModel):
    name: str
    addresses: list[Address]    # 列表中包含嵌套模型

user = User(
    name="张三",
    addresses=[
        {"city": "北京", "street": "长安街"},
        {"city": "上海", "street": "南京路"}
    ]
)
print(user.addresses[0].city)  # → "北京"
```

### 11.2 列表响应模型

```python
class NewsItem(BaseModel):
    id: int
    title: str

class NewsListResponse(BaseModel):
    list: list[NewsItem]         # 新闻列表
    total: int                   # 总数
    has_more: bool               # 是否有更多
```

> 💡 **掘金头条项目案例**——列表响应模型：
> ```python
> # schemas/news.py
> class NewsListResponse(BaseModel):
>     list: list[NewsItemBase]
>     total: int
>     has_more: bool = Field(alias="hasMore")
>
>     model_config = ConfigDict(populate_by_name=True, from_attributes=True)
> ```

### 11.3 多层嵌套

```python
class RelatedNews(BaseModel):
    id: int
    title: str

class NewsDetail(BaseModel):
    id: int
    title: str
    content: str
    related_news: list[RelatedNews]    # 嵌套列表

class ApiResponse(BaseModel):
    code: int
    message: str
    data: NewsDetail                   # 嵌套单个对象
```

---

## 第十二章 在 FastAPI 中的使用模式

### 12.1 请求体模型（Request）

用于定义客户端**发送给服务器**的数据格式：

```python
# 请求模型：定义前端发送的 JSON 格式
class UserRequest(BaseModel):
    username: str
    password: str

@router.post("/register")
async def register(user_data: UserRequest):
    # user_data.username 和 user_data.password 自动可用
    # Pydantic 已经验证了数据类型
    ...
```

### 12.2 响应模型（Response）

用于定义服务器**返回给客户端**的数据格式：

```python
class UserInfoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    nickname: str | None = None
    avatar: str | None = None

@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
    # model_validate 将 ORM User 对象转为 Pydantic UserInfoResponse
    return success_response(data=UserInfoResponse.model_validate(user))
```

### 12.3 请求/响应分离

```python
# 请求模型：包含密码（前端发来的）
class UserRequest(BaseModel):
    username: str
    password: str

# 响应模型：不包含密码（返回给前端的）
class UserInfoResponse(BaseModel):
    id: int
    username: str
    nickname: str | None = None
    # 注意：没有 password 字段！
```

这样即使 ORM 对象包含 password，返回给前端时也会被自动过滤。

### 12.4 统一响应封装

> 💡 **掘金头条项目案例**——统一响应格式：
> ```python
> # utils/response.py
> from fastapi.responses import JSONResponse
> from fastapi.encoders import jsonable_encoder
>
> def success_response(message: str = "success", data=None):
>     content = {
>         "code": 200,
>         "message": message,
>         "data": data
>     }
>     # jsonable_encoder 能处理任何 Python 对象（ORM、Pydantic、datetime 等）
>     return JSONResponse(content=jsonable_encoder(content))
> ```
>
> **返回的 JSON 格式统一为：**
> ```json
> {
>     "code": 200,
>     "message": "获取新闻列表成功",
>     "data": { ... }
> }
> ```

### 12.5 Pydantic 模型在 FastAPI 中的完整角色

```
                    ┌──────────────────┐
                    │   FastAPI 路由    │
                    └────────┬─────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  请求体模型    │  │  查询参数     │  │  Header 参数  │
    │ (Pydantic)   │  │  Query()     │  │  Header()    │
    └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
           │                 │                 │
           ▼                 ▼                 ▼
    ┌──────────────────────────────────────────────┐
    │              业务逻辑处理                       │
    └──────────────────────┬───────────────────────┘
                           │
                           ▼
    ┌──────────────────────────────────────────────┐
    │              响应模型（Pydantic）               │
    │  model_validate(ORM) → model_dump() → JSON   │
    └──────────────────────────────────────────────┘
```

---

## 第十三章 常见错误与调试

### 13.1 ValidationError（验证错误）

```python
from pydantic import BaseModel, ValidationError

class User(BaseModel):
    name: str
    age: int

try:
    user = User(name="张三", age="not_a_number")
except ValidationError as e:
    print(e)
    # 1 validation error for User
    # age
    #   Input should be a valid integer [type=int_parsing, ...]
```

**ValidationError 的有用属性：**
```python
e.errors()        # 返回错误列表
e.error_count()   # 错误数量
e.json()          # JSON 格式的错误信息
```

### 13.2 常见错误类型

| 错误类型 | 原因 | 解决方案 |
|---------|------|----------|
| `missing` | 缺少必填字段 | 提供该字段或设置默认值 |
| `int_parsing` | 字符串无法转为整数 | 检查输入数据 |
| `string_too_short` | 字符串太短 | 检查 min_length |
| `string_too_long` | 字符串太长 | 检查 max_length |
| `value_error` | 自定义验证器报错 | 检查 validator 逻辑 |
| `extra_forbidden` | 传了不允许的额外字段 | 设置 `extra="ignore"` |

### 13.3 ORM 对象转换的常见坑

```python
# ❌ 错误：没有配置 from_attributes
class UserResponse(BaseModel):
    id: int
    name: str

user_response = UserResponse.model_validate(orm_user)
# → ValidationError: 因为默认不接受 ORM 对象

# ✅ 正确：配置 from_attributes
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str

user_response = UserResponse.model_validate(orm_user)  # ✅
```

### 13.4 别名相关的常见坑

```python
class News(BaseModel):
    category_id: int = Field(alias="categoryId")

# ❌ 用字段名创建
News(category_id=1)    # ValidationError: 默认必须用别名

# ✅ 用别名创建
News(categoryId=1)     # ✅

# ✅ 或者配置 populate_by_name
class News(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    category_id: int = Field(alias="categoryId")

News(category_id=1)    # ✅ 现在字段名也可以了
```

### 13.5 model_dump 的 alias 陷阱

```python
news = News(categoryId=1)

# 默认使用字段名（不是别名！）
news.model_dump()
# → {"category_id": 1}

# 要用别名需要显式指定
news.model_dump(by_alias=True)
# → {"categoryId": 1}
```

### 13.6 exclude_unset vs exclude_none

```python
class User(BaseModel):
    name: str = "默认名"
    age: int = None
    bio: str = "默认简介"

user = User(name="张三")

user.model_dump()
# → {"name": "张三", "age": None, "bio": "默认简介"}

user.model_dump(exclude_unset=True)
# → {"name": "张三"}  # 只保留被显式设置的

user.model_dump(exclude_none=True)
# → {"name": "张三", "bio": "默认简介"}  # 去掉了 None

user.model_dump(exclude_unset=True, exclude_none=True)
# → {"name": "张三"}  # 两者结合
```

> 💡 **掘金头条项目案例**——更新用户时的典型用法：
> ```python
> # crud/users.py — 只更新用户实际传了的字段
> user_data.model_dump(exclude_unset=True, exclude_none=True)
> # 前端只传了 {"nickname": "新昵称"}
> # → {"nickname": "新昵称"}
> # 不会把没传的字段也更新到数据库
> ```

---

## 第十四章 项目实战总结

### 14.1 Pydantic 方法速查表

| 方法 | 用途 | 输入 | 输出 |
|------|------|------|------|
| `Model(**kwargs)` | 创建实例 | 关键字参数 | 模型实例 |
| `Model.model_validate()` | 从字典/ORM 创建 | dict / ORM 对象 | 模型实例 |
| `Model.model_validate_json()` | 从 JSON 创建 | JSON 字符串 | 模型实例 |
| `instance.model_dump()` | 转字典 | — | dict |
| `instance.model_dump_json()` | 转 JSON | — | str |
| `instance.model_copy()` | 复制实例 | — | 新的模型实例 |
| `Model.model_fields` | 查看字段信息 | — | dict |

### 14.2 掘金头条项目中的 Pydantic 模型分类

```
schemas/
├── base.py                    # 公共基础模型
│   └── NewsItemBase           #   新闻基础字段（被多处继承）
├── news.py                    # 新闻相关模型
│   ├── NewsListResponse       #   新闻列表响应
│   ├── RelatedNewsResponse    #   相关新闻响应
│   └── NewsDetailResponse     #   新闻详情响应（继承 NewsItemBase）
├── users.py                   # 用户相关模型
│   ├── UserRequest            #   注册/登录请求
│   ├── UserInfoBase           #   用户信息基础
│   ├── UserInfoResponse       #   用户信息响应（继承 UserInfoBase）
│   ├── UserAuthResponse       #   认证响应（token + user_info）
│   ├── UserUpdateRequest      #   更新用户请求
│   └── UserChangePasswordRequest  # 修改密码请求
├── favorite.py                # 收藏相关模型
│   ├── FavoriteCheckResponse  #   收藏状态响应
│   ├── FavoriteAddRequest     #   添加收藏请求
│   ├── FavoriteNewsItemResponse   # 收藏新闻项（继承 NewsItemBase）
│   └── FavoriteListResponse   #   收藏列表响应
└── history.py                 # 历史相关模型
    ├── HistoryAddRequest      #   添加历史请求
    ├── HistoryNewsItemResponse #  历史新闻项（继承 NewsItemBase）
    └── HistoryListResponse    #   历史列表响应
```

### 14.3 核心设计模式总结

#### 模式 1：请求/响应模型分离
```python
# 请求模型：前端发什么
class UserRequest(BaseModel):
    username: str
    password: str

# 响应模型：返回什么（不包含敏感数据）
class UserInfoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    nickname: str | None = None
```

#### 模式 2：基础模型继承
```python
# 基础模型（公共字段）
class NewsItemBase(BaseModel):
    id: int
    title: str
    ...

# 扩展模型（基础 + 新增字段）
class NewsDetailResponse(NewsItemBase):
    content: str
    related_news: list = Field(default_factory=list)
```

#### 模式 3：ORM → Pydantic → JSON 转换链
```python
# ORM 对象 → Pydantic 模型 → 字典 → JSON 响应
pydantic_obj = MyResponse.model_validate(orm_obj)
data_dict = pydantic_obj.model_dump(by_alias=True)
return success_response(data=data_dict)
```

#### 模式 4：ORM → Pydantic → Redis 缓存
```python
# ORM 对象 → Pydantic → JSON 兼容字典 → 存入 Redis
news_data = NewsItemBase.model_validate(orm_item).model_dump(
    mode="json",          # 确保 datetime 等类型可序列化
    by_alias=False        # Redis 用 Python 字段名
)
await set_cache(key, news_data, expire=3600)
```

#### 模式 5：部分更新
```python
# 只更新用户实际修改了的字段
update_data = user_data.model_dump(exclude_unset=True, exclude_none=True)
# {"nickname": "新昵称"} → 只更新 nickname
stmt = update(User).where(...).values(**update_data)
```

### 14.4 ConfigDict 速查——项目中最常用的配置

```python
# 响应模型的标准配置
model_config = ConfigDict(
    from_attributes=True,    # 允许从 ORM 对象取值
    populate_by_name=True    # 字段名和别名都能用
)

# 请求模型通常不需要 model_config
# 因为请求数据来自 JSON，直接用别名就行
```

### 14.5 最佳实践清单

1. **请求和响应使用不同的模型**——不要在响应中暴露密码等敏感字段
2. **使用继承减少重复代码**——公共字段放 Base 模型
3. **始终配置 `from_attributes=True`**——让响应模型能直接转换 ORM 对象
4. **始终配置 `populate_by_name=True`**——避免别名的使用限制
5. **序列化缓存数据时用 `mode="json"`**——确保 datetime 等类型可序列化
6. **缓存数据用 `by_alias=False`**——Redis 是给后端用的，保持 Python 字段名
7. **更新操作使用 `exclude_unset=True`**——只更新用户实际传了的字段
8. **用 `Field(description="...")` 添加字段描述**——提升 Swagger UI 文档的可读性
