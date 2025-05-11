import asyncio
import time
from typing import Optional, List
from datetime import datetime
import traceback
import logging
from pydantic import HttpUrl

from db.database import SessionLocal
from crud import crud_note, crud_task
from models.note import Note as NoteModel
from services.aihubmax_service import get_xhs_note_detail, transcribe_audio, get_qwen_chat_completion, QwenMessage
from utils.media_processor import process_video_to_audio, cleanup_media_files
from core.config import settings
# 从服务层导入增强版获取功能
from services.enhanced_xhs_service import get_enhanced_note_detail

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_note_collection():
    """处理待采集的笔记"""
    db = SessionLocal()
    try:
        # 获取待处理的笔记
        notes = crud_note.get_pending_notes_for_collection(db, limit=5)
        if not notes:
            return
            
        logger.info(f"Found {len(notes)} notes pending collection")
        
        for note in notes:
            try:
                # 获取关联的任务以获取cookie
                task = crud_task.get_task(db, task_id=note.task_id)
                if not task:
                    logger.error(f"Task not found for note {note.id}")
                    crud_note.update_note_with_error(
                        db, note, 
                        "父任务不存在",
                        "error"
                    )
                    continue
                    
                # 使用增强版获取笔记详情
                if note.note_title:
                    logger.info(f"使用增强版API获取笔记 {note.id} ({note.xhs_note_id}) 的详情")
                    response = await get_enhanced_note_detail(
                        note_id=note.xhs_note_id,
                        title=note.note_title,
                        cookie=task.user_cookie,
                        note_type=note.note_type
                    )
                else:
                    # 如果没有标题，回退到原始方法
                    logger.info(f"笔记 {note.id} 没有标题，使用原始API获取详情")
                    note_url = HttpUrl(note.xhs_note_url)
                    response = await get_xhs_note_detail(note_url, task.user_cookie)
                
                # 其余处理逻辑不变
                if not response or response.code != 0 or not response.data:
                    error_msg = f"获取笔记详情失败: {response.msg if response else 'API请求失败'}"
                    logger.error(error_msg)
                    crud_note.update_note_with_error(
                        db, note,
                        error_msg,
                        "error_collection"
                    )
                    continue
                    
                # 处理视频链接
                video_url = None
                if response.data.video_link:
                    # 优先使用API返回的video_link
                    video_url = response.data.video_link
                    
                    # 下载视频和提取音频将在下一步处理
                    video_path = None
                    audio_path = None
                    
                    # 更新笔记，标记为已采集
                    crud_note.update_note_after_collection(
                        db, note, 
                        response.data.model_dump(),
                        video_url
                    )
                else:
                    # 没有视频，标记为已完成且无视频
                    crud_note.update_note_after_collection(
                        db, note,
                        response.data.model_dump()
                    )
                
                # 更新任务统计
                task.notes_processed_count += 1
                if task.notes_processed_count >= task.total_notes_identified:
                    task.status = "collected"
                    task.status_message = "所有笔记已采集完成"
                db.add(task)
                db.commit()
                
                # 防止API调用过于频繁
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error processing note {note.id}: {e}")
                logger.error(traceback.format_exc())
                crud_note.update_note_with_error(
                    db, note,
                    f"处理笔记时出错: {str(e)}",
                    "error_collection"
                )
                
    except Exception as e:
        logger.error(f"Error in process_note_collection: {e}")
        logger.error(traceback.format_exc())
    finally:
        db.close()

async def process_note_transcription():
    """处理视频转录"""
    db = SessionLocal()
    try:
        # 获取已下载视频的笔记
        notes = crud_note.get_pending_notes_for_transcription(db, limit=2)
        if not notes:
            return
            
        logger.info(f"Found {len(notes)} notes pending transcription")
        
        for note in notes:
            try:
                video_url = note.video_url_internal
                if not video_url:
                    crud_note.update_note_with_error(
                        db, note,
                        "笔记没有视频链接",
                        "error_transcription"
                    )
                    continue
                
                # 添加多次尝试下载视频的逻辑
                max_download_attempts = 3
                for download_attempt in range(max_download_attempts):
                    try:
                        video_path, audio_path = process_video_to_audio(video_url)
                        if audio_path:
                            break  # 下载成功，跳出循环
                            
                        logger.warning(f"下载视频或提取音频失败 (尝试 {download_attempt+1}/{max_download_attempts})")
                        if download_attempt < max_download_attempts - 1:
                            logger.info(f"将在10秒后重试下载")
                            await asyncio.sleep(10)
                    except Exception as e:
                        logger.error(f"下载视频过程中发生异常: {e}")
                        if download_attempt < max_download_attempts - 1:
                            logger.info(f"将在10秒后重试下载")
                            await asyncio.sleep(10)
                
                if not audio_path:
                    crud_note.update_note_with_error(
                        db, note,
                        "无法下载视频或提取音频",
                        "error_transcription"
                    )
                    continue
                
                # 转录也使用多次尝试
                max_transcribe_attempts = 3
                for transcribe_attempt in range(max_transcribe_attempts):
                    try:
                        # 使用不同的转录模型
                        models = ["whisper-1", "large", "medium"]  # 假设支持这些模型
                        model_to_use = models[min(transcribe_attempt, len(models)-1)]
                        
                        logger.info(f"使用模型 {model_to_use} 尝试转录 (尝试 {transcribe_attempt+1}/{max_transcribe_attempts})")
                        transcription_response = await transcribe_audio(audio_path, model=model_to_use)
                        
                        if transcription_response:
                            break  # 转录成功，跳出循环
                            
                        if transcribe_attempt < max_transcribe_attempts - 1:
                            logger.info(f"转录失败，将在10秒后使用不同模型重试")
                            await asyncio.sleep(10)
                    except Exception as e:
                        logger.error(f"转录过程中发生异常: {e}")
                        if transcribe_attempt < max_transcribe_attempts - 1:
                            logger.info(f"将在10秒后重试转录")
                            await asyncio.sleep(10)
                
                # 清理临时文件
                cleanup_media_files([video_path, audio_path])
                
                if not transcription_response:
                    crud_note.update_note_with_error(
                        db, note,
                        "音频转录失败",
                        "error_transcription"
                    )
                    continue
                
                # 更新笔记
                crud_note.update_note_after_transcription(
                    db, note, 
                    transcription_response.text
                )
                
                # 防止API调用过于频繁
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error transcribing note {note.id}: {e}")
                logger.error(traceback.format_exc())
                crud_note.update_note_with_error(
                    db, note,
                    f"转录处理时出错: {str(e)}",
                    "error_transcription"
                )
    
    except Exception as e:
        logger.error(f"Error in process_note_transcription: {e}")
        logger.error(traceback.format_exc())
    finally:
        db.close()

async def process_note_analysis():
    """处理AI分析"""
    db = SessionLocal()
    try:
        # 获取已转录的笔记
        notes = crud_note.get_pending_notes_for_analysis(db, limit=2)
        if not notes:
            return
            
        logger.info(f"Found {len(notes)} notes pending analysis")
        
        for note in notes:
            try:
                transcript = note.video_transcript_text
                if not transcript:
                    crud_note.update_note_with_error(
                        db, note,
                        "笔记没有转录文本",
                        "error_analysis"
                    )
                    continue
                
                # 准备提示词
                system_prompt = """
                你是一位专业的内容分析师，擅长分析短视频文案并提供改进建议。请对以下文案进行详细分析，包括：
                1. 文案的核心卖点和情感诉求
                2. 文案的叙事结构、节奏和钩子
                3. 语言风格和目标受众群体
                4. 号召性用语的效果
                5. 至少3点具体的改进建议
                
                返回一个结构化的分析报告，用标题分隔每个部分。
                """
                
                user_prompt = f"""
                以下是需要分析的视频文案：
                
                {transcript}
                
                请提供详细分析。
                """
                
                # 调用千问API进行分析
                messages = [
                    QwenMessage(role="system", content=system_prompt),
                    QwenMessage(role="user", content=user_prompt)
                ]
                
                response = await get_qwen_chat_completion(messages)
                
                if not response or not response.choices:
                    crud_note.update_note_with_error(
                        db, note,
                        "AI分析失败",
                        "error_analysis"
                    )
                    continue
                
                analysis_text = response.choices[0].message.content
                
                # 更新笔记
                crud_note.update_note_after_analysis(
                    db, note,
                    analysis_text
                )
                
                # 防止API调用过于频繁
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error analyzing note {note.id}: {e}")
                logger.error(traceback.format_exc())
                crud_note.update_note_with_error(
                    db, note,
                    f"AI分析时出错: {str(e)}",
                    "error_analysis"
                )
    
    except Exception as e:
        logger.error(f"Error in process_note_analysis: {e}")
        logger.error(traceback.format_exc())
    finally:
        db.close()

async def run_background_tasks():
    """运行所有后台任务"""
    while True:
        try:
            # 依次执行各个处理步骤
            await process_note_collection()
            await process_note_transcription()
            await process_note_analysis()
            
            # 休息一段时间再继续循环
            await asyncio.sleep(settings.BACKGROUND_TASK_INTERVAL_SECONDS)
            
        except Exception as e:
            logger.error(f"Error in background tasks: {e}")
            logger.error(traceback.format_exc())
            await asyncio.sleep(10)  # 发生错误时短暂休息