import re
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import traceback

from schemas.task import Task, TaskCreate, TaskUpdate
from schemas.note import Note, NoteCreate
from crud import crud_task, crud_note
from api import deps
from models.user import User as UserModel
from services.aihubmax_service import get_xhs_user_posts
from utils.url_parser import extract_blogger_id_from_url

router = APIRouter()

async def process_task_notes(task_id: int, db: Session):
    """
    后台任务：获取博主的笔记列表并筛选符合条件的笔记
    """
    try:
        # 获取任务信息
        task = crud_task.get_task(db, task_id=task_id)
        if not task:
            print(f"Error: Task {task_id} not found")
            return
        
        # ===== 取消注释，启用自动处理逻辑 =====
        # 获取博主ID
        blogger_id = task.blogger_id
        if not blogger_id:
            print(f"Error: Blogger ID not found for task {task_id}")
            task.status = "failed"
            task.status_message = "无法解析博主ID"
            db.add(task)
            db.commit()
            return
            
        # 调用服务获取博主笔记列表
        response = await get_xhs_user_posts(blogger_id, task.user_cookie)
        if not response or response.code != 0:
            error_msg = f"获取博主笔记列表失败: {response.msg if response else 'API请求失败'}"
            print(f"Error: {error_msg}")
            task.status = "failed"
            task.status_message = error_msg
            db.add(task)
            db.commit()
            return
            
        # 应用筛选规则
        scraping_rules = task.scraping_rules or {}
        note_type = scraping_rules.get("type", "video")  # 默认筛选视频类型
        sort_by = scraping_rules.get("sort_by", "likes")  # 默认按点赞量排序
        count = scraping_rules.get("count", 10)  # 默认获取前10条
        
        filtered_notes = []
        if response.data and response.data.notes:
            notes = response.data.notes
            
            # 筛选指定类型
            if note_type != "all":
                if note_type == "video":
                    # 视频类型筛选
                    notes = [note for note in notes if getattr(note, "type", "") == "video"]
                elif note_type == "normal":
                    # 图文类型筛选 - 接受API返回的normal类型
                    notes = [note for note in notes if getattr(note, "type", "") != "video"]
                # TODO: 提供的主页信息API默认只返回30条笔记
                # 目前筛选后笔记数量太少，可能是因为默认只获取了首页的30条数据

            # 按点赞量排序 (需要将字符串转为数字进行排序)
            if sort_by == "likes" and notes:
                def get_likes_count(note):
                    if not note.interact_info or not note.interact_info.liked_count:
                        return 0
                    # 转换形如 "1.2万" 的字符串到数字
                    likes_str = note.interact_info.liked_count
                    try:
                        if "万" in likes_str:
                            return float(likes_str.replace("万", "")) * 10000
                        return float(likes_str)
                    except ValueError:
                        return 0
                
                notes = sorted(notes, key=get_likes_count, reverse=True)
            
            # 限制数量
            filtered_notes = notes[:count]
        
        # 更新任务状态
        if not filtered_notes:
            task.status = "no_notes_found"
            task.status_message = "未找到符合条件的笔记"
            db.add(task)
            db.commit()
            return
            
        # 将筛选后的笔记保存到数据库
        task.total_notes_identified = len(filtered_notes)
        task.notes_processed_count = 0
        task.status = "notes_identified"
        task.status_message = f"已找到{len(filtered_notes)}条符合条件的笔记"
        
        for note in filtered_notes:
            # 构建笔记URL
            note_url = f"https://www.xiaohongshu.com/explore/{note.note_id}"
            
            # 解析点赞数
            likes_count = 0
            if note.interact_info and note.interact_info.liked_count:
                likes_str = note.interact_info.liked_count
                try:
                    if "万" in likes_str:
                        likes_count = int(float(likes_str.replace("万", "")) * 10000)
                    else:
                        likes_count = int(float(likes_str))
                except ValueError:
                    likes_count = 0
            
            # 创建笔记记录 - 确保保存标题
            # 确定笔记类型 - 使用原始类型
            detected_type = getattr(note, "type", "")
            # 如果类型不是video，统一为normal
            if detected_type != "video":
                detected_type = "normal"
            
            note_create = NoteCreate(
                task_id=task.id,
                xhs_note_id=note.note_id,
                xhs_note_url=note_url,
                note_type=detected_type,
                note_title=getattr(note, "title", "无标题"),
                original_likes_count=likes_count,
                processing_status="pending_collection"
            )
            crud_note.create_note(db=db, note_in=note_create)
        
        # 更新任务状态
        db.add(task)
        db.commit()
        # ===== 注释结束 =====
        
    except Exception as e:
        print(f"Error processing task notes: {e}")
        print(traceback.format_exc())
        # 更新任务状态为失败
        try:
            task = crud_task.get_task(db, task_id=task_id)
            if task:
                task.status = "failed"
                task.status_message = f"处理笔记时出错: {str(e)}"
                db.add(task)
                db.commit()
        except Exception as update_err:
            print(f"Error updating task status: {update_err}")

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_new_task(
    *,
    db: Session = Depends(deps.get_db),
    task_in: TaskCreate,
    background_tasks: BackgroundTasks,
    current_user: UserModel = Depends(deps.get_current_active_user)
):
    """
    为已登录用户创建一个新任务。
    任务创建后，会立即异步获取博主的笔记列表。
    """
    user_id = current_user.id
    
    # 确保任务有默认规则
    if not task_in.scraping_rules:
        task_in.scraping_rules = {
            "type": "video",     # 默认只抓取视频类
            "sort_by": "likes",  # 默认按点赞排序
            "count": 10          # 默认抓取前10条
        }
    
    # 创建任务
    task = crud_task.create_task(db=db, task_in=task_in, user_id=user_id)
    
    # 在后台处理笔记列表获取
    background_tasks.add_task(process_task_notes, task.id, db)
    
    return task

@router.get("/{task_id}", response_model=Task)
def read_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    current_user: UserModel = Depends(deps.get_current_active_user)
):
    """
    按 ID 获取特定任务，该任务属于当前用户，并包含其笔记列表。
    """
    task = crud_task.get_task(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务未找到")
    if task.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有足够的权限访问此任务。")
    
    # 获取任务的笔记列表
    notes = crud_note.get_notes_by_task(db, task_id=task_id)
    
    # 将笔记列表添加到任务对象中
    task.notes = notes
    
    return task

@router.get("/", response_model=List[Task])
def read_tasks_for_user(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(deps.get_current_active_user)
):
    """
    检索当前用户的任务。
    """
    tasks = crud_task.get_tasks_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return tasks

@router.put("/{task_id}", response_model=Task)
def update_existing_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    task_in: TaskUpdate,
    current_user: UserModel = Depends(deps.get_current_active_user)
):
    """
    更新当前用户拥有的现有任务。
    """
    db_task = crud_task.get_task(db, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务未找到")
    if db_task.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有足够的权限更新此任务。")
    
    updated_task = crud_task.update_task(db=db, db_task=db_task, task_in=task_in)
    return updated_task

@router.delete("/{task_id}", response_model=Task)
def delete_existing_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    current_user: UserModel = Depends(deps.get_current_active_user)
):
    """
    删除当前用户拥有的任务。
    """
    task_to_delete = crud_task.get_task(db, task_id=task_id)
    if not task_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务未找到")
    if task_to_delete.user_id != current_user.id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有足够的权限删除此任务。")

    deleted_task = crud_task.delete_task(db=db, task_id=task_id, user_id=current_user.id)
    if not deleted_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务未找到或已被删除。")
    return deleted_task

@router.get("/notes/{note_id}", response_model=Note)
def read_note(
    *,
    db: Session = Depends(deps.get_db),
    note_id: int,
    current_user: UserModel = Depends(deps.get_current_active_user)
):
    """
    按 ID 获取特定笔记，该笔记属于当前用户。
    """
    note = crud_note.get_note(db, note_id=note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="笔记未找到")
    
    # 验证用户是否有权访问该笔记
    task = crud_task.get_task(db, task_id=note.task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有足够的权限访问此笔记。")
    
    return note