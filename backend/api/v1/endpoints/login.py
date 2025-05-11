from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # FastAPI 提供的表单类，用于接收 username 和 password
from sqlalchemy.orm import Session

from api import deps
from core import security
from core.config import settings
from crud import crud_user
from schemas.token import Token

router = APIRouter()

@router.post("/login/access-token", response_model=Token)
async def login_for_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends() # username 和 password 从表单数据中获取
):
    """
    OAuth2兼容的token登录，获取access token。
    需要发送 x-www-form-urlencoded 表单数据，包含 username 和 password。
    """
    user = crud_user.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}