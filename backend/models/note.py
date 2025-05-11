from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, JSON
from sqlalchemy.orm import relationship

from db.base_class import Base # 确保路径正确

class Note(Base):
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False) # 注意表名是 tasks
    xhs_note_id = Column(String(255), nullable=False, index=True) # 考虑与 task_id 组合唯一
    xhs_note_url = Column(Text, nullable=False)
    note_type = Column(String(50), nullable=True)
    original_likes_count = Column(Integer, nullable=True)
    processing_status = Column(String(50), nullable=False, default='pending_collection', index=True)
    raw_note_details = Column(JSON, nullable=True)
    video_url_internal = Column(Text, nullable=True)
    video_transcript_text = Column(Text, nullable=True)
    analysis_result_text = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    # created_at 和 updated_at 从 Base 类继承
    details_collected_at = Column(DateTime, nullable=True)
    video_downloaded_at = Column(DateTime, nullable=True)
    transcribed_at = Column(DateTime, nullable=True)
    analyzed_at = Column(DateTime, nullable=True)

    task = relationship("Task", back_populates="notes")

    def __repr__(self):
        return f"<Note(id={self.id}, task_id={self.task_id}, xhs_note_id='{self.xhs_note_id}', status='{self.processing_status}')>"