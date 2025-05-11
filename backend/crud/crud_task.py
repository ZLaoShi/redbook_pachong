from sqlalchemy.orm import Session
from typing import Optional
import re # For extracting blogger_id

from models.task import Task as TaskModel # SQLAlchemy model
from schemas.task import TaskCreate, TaskUpdate # Pydantic schemas

def extract_blogger_id_from_url(url: str) -> Optional[str]:
    """
    Extracts the Xiaohongshu blogger ID from a profile URL.
    Example: https://www.xiaohongshu.com/user/profile/5a0a2f7fe8ac2b7abfb21ead
    Returns: 5a0a2f7fe8ac2b7abfb21ead
    """
    match = re.search(r"/user/profile/([^/?]+)", str(url))
    if match:
        return match.group(1)
    return None

def get_task(db: Session, task_id: int) -> Optional[TaskModel]:
    return db.query(TaskModel).filter(TaskModel.id == task_id).first()

def get_tasks_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[TaskModel]:
    return db.query(TaskModel).filter(TaskModel.user_id == user_id).offset(skip).limit(limit).all()

def create_task(db: Session, *, task_in: TaskCreate, user_id: int) -> TaskModel:
    blogger_id = extract_blogger_id_from_url(str(task_in.blogger_profile_url))
    
    db_task = TaskModel(
        **task_in.model_dump(), # Pydantic V2
        user_id=user_id,
        blogger_id=blogger_id,
        status="pending" # Initial status
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, *, db_task: TaskModel, task_in: TaskUpdate) -> TaskModel:
    update_data = task_in.model_dump(exclude_unset=True) # Pydantic V2
    
    if "blogger_profile_url" in update_data:
        db_task.blogger_id = extract_blogger_id_from_url(str(update_data["blogger_profile_url"]))

    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, *, task_id: int, user_id: int) -> Optional[TaskModel]:
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == user_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
        return db_task
    return None