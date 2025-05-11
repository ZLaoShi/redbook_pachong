from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.note import Note as NoteModel
from schemas.note import NoteCreate, NoteUpdate

def get_note(db: Session, note_id: int) -> Optional[NoteModel]:
    return db.query(NoteModel).filter(NoteModel.id == note_id).first()

def get_note_by_xhs_id(db: Session, xhs_note_id: str) -> Optional[NoteModel]:
    return db.query(NoteModel).filter(NoteModel.xhs_note_id == xhs_note_id).first()

def get_notes_by_task(db: Session, task_id: int, skip: int = 0, limit: int = 100) -> List[NoteModel]:
    return db.query(NoteModel).filter(NoteModel.task_id == task_id).offset(skip).limit(limit).all()

def get_pending_notes_for_collection(db: Session, limit: int = 10) -> List[NoteModel]:
    """获取待采集的笔记"""
    return db.query(NoteModel).filter(
        NoteModel.processing_status == "pending_collection"
    ).order_by(NoteModel.created_at.asc()).limit(limit).all()

def get_pending_notes_for_transcription(db: Session, limit: int = 5) -> List[NoteModel]:
    """获取待转录的笔记"""
    return db.query(NoteModel).filter(
        NoteModel.processing_status == "video_downloaded",
        NoteModel.video_url_internal.isnot(None)
    ).order_by(NoteModel.created_at.asc()).limit(limit).all()

def get_pending_notes_for_analysis(db: Session, limit: int = 5) -> List[NoteModel]:
    """获取待分析的笔记"""
    return db.query(NoteModel).filter(
        NoteModel.processing_status == "transcribed",
        NoteModel.video_transcript_text.isnot(None)
    ).order_by(NoteModel.created_at.asc()).limit(limit).all()

def create_note(db: Session, note_in: NoteCreate) -> NoteModel:
    db_note = NoteModel(**note_in.model_dump())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def update_note(db: Session, db_note: NoteModel, note_in: NoteUpdate) -> NoteModel:
    update_data = note_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_note, field, value)
    
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def update_note_after_collection(
    db: Session, 
    db_note: NoteModel,
    raw_details: Dict[str, Any],
    video_url: Optional[str] = None
) -> NoteModel:
    """收集笔记详情后更新笔记"""
    db_note.raw_note_details = raw_details
    db_note.details_collected_at = datetime.now()
    
    if video_url:
        db_note.video_url_internal = video_url
        db_note.processing_status = "video_downloaded"
        db_note.video_downloaded_at = datetime.now()
    else:
        db_note.processing_status = "completed_no_video"
    
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def update_note_after_transcription(
    db: Session,
    db_note: NoteModel,
    transcript_text: str
) -> NoteModel:
    """转录完成后更新笔记"""
    db_note.video_transcript_text = transcript_text
    db_note.processing_status = "transcribed"
    db_note.transcribed_at = datetime.now()
    
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def update_note_after_analysis(
    db: Session,
    db_note: NoteModel,
    analysis_result: str
) -> NoteModel:
    """AI分析完成后更新笔记"""
    db_note.analysis_result_text = analysis_result
    db_note.processing_status = "completed"
    db_note.analyzed_at = datetime.now()
    
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def update_note_with_error(
    db: Session,
    db_note: NoteModel,
    error_message: str,
    status: str = "error"
) -> NoteModel:
    """更新笔记错误状态"""
    db_note.error_message = error_message
    db_note.processing_status = status
    
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note