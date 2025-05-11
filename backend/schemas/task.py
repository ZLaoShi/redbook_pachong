from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from .user import User # Assuming user.py is in the same schemas directory
from .note import Note

class TaskBase(BaseModel):
    blogger_profile_url: HttpUrl
    user_cookie: str # Consider security implications if storing raw cookies long-term
    scraping_rules: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {"type": "video", "sort_by": "likes", "count": 10}
    )

class TaskCreate(TaskBase):
    pass

class Task(TaskBase): # Schema for reading/returning task data
    id: int
    user_id: int
    blogger_id: Optional[str] = None
    status: str
    status_message: Optional[str] = None
    total_notes_identified: int
    notes_processed_count: int
    created_at: datetime
    updated_at: datetime
    owner: Optional[User] = None # To include user details when returning a task
    notes: List[Note] = []  # 添加 notes 字段

    model_config = {
        "from_attributes": True # For Pydantic V2
    }

class TaskUpdate(BaseModel): # For potential future use
    blogger_profile_url: Optional[HttpUrl] = None
    user_cookie: Optional[str] = None
    scraping_rules: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    status_message: Optional[str] = None
    total_notes_identified: Optional[int] = None
    notes_processed_count: Optional[int] = None
