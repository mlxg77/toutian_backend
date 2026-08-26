from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from models.users import User
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UserUpdateRequest, UserChangePasswordRequest

from config.db_conf import get_db, AsyncSessionLocal
from crud import users
from utils.response import success_response
from utils.auth import get_current_user

router = APIRouter(prefix="/api/user", tags=["users"])


@router.post("/register")
async def register(
        user_data: UserRequest,
        background_tasks: BackgroundTasks,              # ← 后台任务对象，FastAPI 自动注入
        db: AsyncSession = Depends(get_db)):  # 用户信息 和 db
    # 注册逻辑：验证用户是否存在 -> 创建用户 → 生成 Token  → 响应结果
    existing_user = await users.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在")
    user = await users.create_user(db, user_data)
    token = await users.create_token(db, user.id)

    # ⭐ 注册成功之后，把「发送欢迎邮件」扔进后台任务
    # 这样前端不用等邮件发送，路由直接返回
    # 注意：只传数据（user.id、username），不要传 db！
    # background_tasks.add_task(right_welcome_email, user.id, user_data.username)
    # ❌ 错误写法：background_tasks.add_task(wrong_welcome_email, db, user.id)

    # model_validate 校验数据并转换为指定类型，和 from_attributes=True 一起使用可以对 orm 数据进行转换
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="注册成功", data=response_data)


# ==================== 伪代码区：理解 session 生命周期 ====================
# 以下全是示意代码，不会真的执行，看懂就删掉

# ❌ 错误示范：把路由里的 db 传给后台任务
async def wrong_welcome_email(db: AsyncSession, user_id: int):
    """
    为什么错？
    - 后台任务在「响应发回前端之后」才跑
    - 此时 get_db 的 finally 早就执行过了，session 已 close
    - 再 db.add / db.commit 会报 "Instance is not bound to a Session"
    """
    log = {"user_id": user_id, "type": "welcome", "status": "sent"}
    db.add(log)               # 💥 session 已关闭，报错
    await db.commit()         # 💥 session 已关闭，报错


# ✅ 正确示范：后台任务自己开 session
async def right_welcome_email(user_id: int, email: str):
    """
    后台任务完全独立，不依赖路由里的 db：
    - 用 async with AsyncSessionLocal() as db 自己建一个
    - 跑完自动 commit + close
    """
    # 第一步：干「不需要数据库」的事（比如调第三方邮件接口）
    print(f"正在给 {email} 发送欢迎邮件...")
    # await send_email_via_smtp(email, "欢迎加入掘金头条！")

    # 第二步：自己开一个 session，写一条发送日志到数据库
    # Depends 只对路由生效，所以不能通过 Depends(get_db) 获取 db
    #     async with   AsyncSessionLocal()    as    db:
    #       ↑              ↑                   ↑     ↑
    #    异步地      创建/进入 一个对象    把返回值  绑定到这个变量名
    # ':'："这句话我说完了，下面缩进的代码都是这个语句管的范围"
    async with AsyncSessionLocal() as db:
        log = {"user_id": user_id, "type": "welcome", "status": "sent"}
        db.add(log)
        await db.commit()
    # async with 结束 → 自动 close，跟路由的 session 互不干扰


# 在路由里的调用方式对比（假设 register 要用后台任务）：
# background_tasks.add_task(wrong_welcome_email, db, user.id)        ❌ 传了 db
# background_tasks.add_task(right_welcome_email, user.id, user.email) ✅ 只传数据
# ==================== 伪代码区结束 ====================


@router.post("/login")
async def login(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    # 登录逻辑：验证用户是否存在 -> 验证密码 -> 生成 Token  → 响应结果
    user = await users.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token = await users.create_token(db, user.id)
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="登录成功啦", data=response_data)


# 查Token查用户 → 封装crud → 功能整合成一个工具函数 → 路由导入使用: 依赖注入
# FastAPI 在执行路由函数之前，会先把所有 Depends(...) 跑一遍，拿到结果再注入参数。
# 为什么get_current_user用注入的方式，不用函数的方式：
#   直接调用技术上可行，但会把 Depends 帮你解决的 3 件事（参数复用、测试 mock、缓存）全打回原形。
#   Depends(get_current_user) 看起来"绕"，实际上是 FastAPI 专门设计的、最简洁、最可测试、最高效的写法。
@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
    return success_response(message="获取用户信息成功", data=UserInfoResponse.model_validate(user))


# 修改用户信息：验证Token → 更新（用户输入数据 put 提交 → 请求体参数 → 定义Pydantic模型类） → 响应结果
# 参数：用户输入的 + 验证Token的 + db（调用更新的方法）
@router.put("/update")
async def update_user_info(user_data: UserUpdateRequest, 
                           user: User = Depends(get_current_user),
                           db: AsyncSession = Depends(get_db)):
    user = await users.update_user(db, user.username, user_data)
    return success_response(message="更新用户信息成功", data=UserInfoResponse.model_validate(user))


@router.put("/password")
async def update_password(
        password_data: UserChangePasswordRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    res_change_pwd = await users.change_password(db, user, password_data.old_password, password_data.new_password)
    if not res_change_pwd:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="修改密码失败，请稍后再试")
    return success_response(message="修改密码成功")
