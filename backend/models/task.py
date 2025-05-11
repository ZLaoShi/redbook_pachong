from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, JSON
from sqlalchemy.orm import relationship

from db.base_class import Base # 确保路径正确

class Task(Base):
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) # 注意表名是 users
    blogger_profile_url = Column(Text, nullable=False)
    blogger_id = Column(String(255), nullable=True, index=True)
    user_cookie = Column(Text, nullable=False) # 考虑加密
    scraping_rules = Column(JSON, nullable=True)
    status = Column(String(50), nullable=False, default='pending', index=True)
    status_message = Column(Text, nullable=True)
    total_notes_identified = Column(Integer, default=0)
    notes_processed_count = Column(Integer, default=0)
    # created_at 和 updated_at 从 Base 类继承

    owner = relationship("User", back_populates="tasks")
    notes = relationship("Note", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Task(id={self.id}, user_id={self.user_id}, status='{self.status}')>"