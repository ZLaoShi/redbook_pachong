from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from db.base_class import Base # 确保路径正确

class User(Base):
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    # created_at 和 updated_at 从 Base 类继承

    tasks = relationship("Task", back_populates="owner")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"