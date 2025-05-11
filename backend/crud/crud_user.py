from sqlalchemy.orm import Session
from typing import Optional

from core.security import get_password_hash
from models.user import User as UserModel # SQLAlchemy 模型
from schemas.user import UserCreate # Pydantic schema

def get_user_by_username(db: Session, username: str) -> Optional[UserModel]:
    """
    根据用户名从数据库中获取用户
    """
    return db.query(UserModel).filter(UserModel.username == username).first()

def create_user(db: Session, user: UserCreate) -> UserModel:
    """
    在数据库中创建新用户
    """
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user) # 刷新以获取数据库生成的数据，如 id, created_at
    return db_user