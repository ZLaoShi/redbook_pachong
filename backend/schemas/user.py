from pydantic import BaseModel, Field
from typing import Optional

# 基础用户模型，不包含敏感信息
class UserBase(BaseModel):
    username: str

# 创建用户时需要提供密码
class UserCreate(UserBase):
    password: str = Field(..., min_length=6) # 密码至少6位

# 从数据库读取用户数据并返回给API时使用的模型
# 继承自UserBase，并添加id等字段
class User(UserBase):
    id: int
    # is_active: bool # 如果需要激活状态
    # is_superuser: bool # 如果需要超级用户状态

    class Config:
        from_attributes = True # Pydantic V2 (旧版 orm_mode = True)