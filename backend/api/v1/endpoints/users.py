from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api import deps
from crud import crud_user
from schemas.user import User, UserCreate # 导入 Pydantic schemas
from models.user import User as UserModel # 导入 SQLAlchemy model (如果需要在响应中返回)

router = APIRouter()

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user_registration(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate
):
    """
    创建新用户。
    """
    user = crud_user.get_user_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this username already exists in the system.",
        )
    new_user = crud_user.create_user(db=db, user=user_in)
    return new_user

@router.get("/me", response_model=User)
async def read_users_me(
    current_user: UserModel = Depends(deps.get_current_active_user)
):
    """
    获取当前用户信息。
    这是一个受保护的端点，需要有效的 JWT。
    """
    return current_user