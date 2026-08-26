import jwt
from datetime import datetime, timedelta, timezone

# 生产环境建议放 .env，不要硬编码在代码里
# 改完记得重启服务才生效
SECRET_KEY = "toutiao-backend-secret-key-change-me-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7


def create_access_token(user_id: int, expires_days: int = ACCESS_TOKEN_EXPIRE_DAYS) -> str:
    """
    生成 JWT access token
    :param user_id: 用户 id，会写入 payload
    :param expires_days: 过期天数，默认 7 天
    :return: JWT 字符串
    """
    now = datetime.now(timezone.utc)
    payload = {
        "user_id": user_id,      # 用户标识
        "iat": now,              # issued at，签发时间
        "exp": now + timedelta(days=expires_days),   # 过期时间
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str) -> int | None:
    """
    验证 JWT，成功返回 user_id，失败（过期/篡改/格式错）返回 None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("user_id")
    except jwt.ExpiredSignatureError:
        # 已过期
        return None
    except jwt.InvalidTokenError:
        # 签名无效 / 格式错误 / 被篡改
        return None
