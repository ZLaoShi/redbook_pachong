from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict, Any
from datetime import datetime

class NoteBase(BaseModel):
    task_id: int
    xhs_note_id: str
    xhs_note_url: str
    note_type: Optional[str] = None
    # TODO: 添加note_title字段用于搜索
    # note_title: Optional[str] = None
    original_likes_count: Optional[int] = None
    processing_status: str = "pending_collection"
    
class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    raw_note_details: Optional[Dict[str, Any]] = None
    video_url_internal: Optional[str] = None
    video_transcript_text: Optional[str] = None
    analysis_result_text: Optional[str] = None
    processing_status: Optional[str] = None
    error_message: Optional[str] = None
    details_collected_at: Optional[datetime] = None
    video_downloaded_at: Optional[datetime] = None
    transcribed_at: Optional[datetime] = None
    analyzed_at: Optional[datetime] = None

class Note(NoteBase):
    id: int
    raw_note_details: Optional[Dict[str, Any]] = None
    video_url_internal: Optional[str] = None
    video_transcript_text: Optional[str] = None
    analysis_result_text: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    details_collected_at: Optional[datetime] = None
    video_downloaded_at: Optional[datetime] = None
    transcribed_at: Optional[datetime] = None
    analyzed_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
    }