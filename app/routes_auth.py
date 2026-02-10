from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from .schemas import LoginRequest, Token, User

SECRET_KEY = "CHANGE_ME_TO_A_RANDOM_SECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

router = APIRouter(prefix="/api/auth", tags=["auth"])


# 为了简单起见，这里用内存中的单用户，后续可以接数据库。
# 当前仅用于开发联调，不做真正的密码加密。
fake_user_db = {
    "admin": {
        "id": 1,
        "username": "admin",
        "password": "123456",
    }
}


def authenticate_user(username: str, password: str) -> Optional[User]:
    user_record = fake_user_db.get(username)
    if not user_record:
        return None
    if password != user_record["password"]:
        return None
    return User(id=user_record["id"], username=user_record["username"])


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="未登录或登录已过期",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("uid")
        if username is None or user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return User(id=user_id, username=username)


@router.post("/login")
async def login(body: LoginRequest, response: Response):
    """
    登录接口（JSON 请求体），严格兼容前端当前的调用方式与期望返回：
    - URL：POST /api/auth/login
    - Body：{ "username": "...", "password": "..." }

    成功：
    HTTP 200
    {
      "ok": true,
      "token": "<jwt>",
      "user": { "username": "xxx" }
    }

    账号或密码错误：
    HTTP 401
    { "ok": false, "message": "用户名或密码错误" }

    服务器异常：
    HTTP 500
    { "ok": false, "message": "登录失败，请稍后重试" }
    """
    try:
        user = authenticate_user(body.username, body.password)
        if not user:
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return {"ok": False, "message": "用户名或密码错误"}

        access_token = create_access_token(data={"sub": user.username, "uid": user.id})
        return {
            "ok": True,
            "token": access_token,
            "user": {"username": user.username},
        }
    except Exception:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"ok": False, "message": "登录失败，请稍后重试"}


@router.get("/me")
async def read_current_user(current_user: User = Depends(get_current_user)):
    """GET /api/auth/me，返回 { "ok": true, "user": { "username": "string" } }"""
    return {"ok": True, "user": {"username": current_user.username}}

