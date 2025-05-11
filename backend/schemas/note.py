from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
from datetime import datetime

class NoteBase(BaseModel):
    xhs_note_id: str
    xhs_note_url: HttpUrl
    note_title: Optional[str] = None
    note_type: Optional[str] = None
    original_likes_count: Optional[int] = 0

class NoteCreate(NoteBase):
    task_id: int

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
    task_id: int
    processing_status: str
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