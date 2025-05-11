from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from core import security
from core.config import settings
from crud import crud_user
from db.database import SessionLocal
from models.user import User as UserModel
from schemas.token import TokenData

# OAuth2PasswordBearer 会从请求的 Authorization header 中提取 token
# tokenUrl 指向获取 token 的端点路径 (我们稍后会创建它)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")

def get_db() -> Generator:
    """
    依赖项：为每个请求提供一个数据库会话，并在请求完成后关闭它。
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> UserModel:
    """
    依赖项：从 token 中解析并获取当前用户。
    如果 token 无效或用户不存在，则抛出 HTTPException。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.decode_access_token(token)
        if payload is None:
            raise credentials_exception
        username: Optional[str] = payload.get("sub") # 我们将在创建 token 时使用 "sub" 作为 username
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except (JWTError, ValidationError):
        raise credentials_exception

    user = crud_user.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    """
    依赖项：获取当前活动用户。
    如果需要用户激活状态检查，可以在这里添加。
    目前简单返回当前用户。
    """
    # if not current_user.is_active: # 如果有 is_active 字段
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user