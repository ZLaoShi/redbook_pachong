import httpx
import os
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, HttpUrl, Field

# 从项目的 core.config 导入 settings 对象
from core.config import settings

# === Pydantic Models for XHS User Posts API ===
class XHSUserPostRequest(BaseModel):
    cookie: str
    user_id: str

class XHSNoteInteractInfo(BaseModel):
    liked: Optional[bool] = None
    liked_count: Optional[str] = None
    sticky: Optional[bool] = None

class XHSNoteBasicInfo(BaseModel):
    note_id: str
    type: Optional[str] = None
    title: Optional[str] = None
    cover: Optional[HttpUrl] = None
    interact_info: Optional[XHSNoteInteractInfo] = None

class XHSUserPostData(BaseModel):
    notes: Optional[List[XHSNoteBasicInfo]] = None
    has_more: Optional[bool] = None
    cursor: Optional[str] = None

class XHSUserPostResponse(BaseModel):
    code: int
    msg: str
    data: Optional[XHSUserPostData] = None

# === Pydantic Models for XHS Note Detail API ===
class XHSNoteDetailRequest(BaseModel):
    cookie: Optional[str] = None
    url: str

class XHSNoteContentData(BaseModel):
    title: Optional[str] = None
    desc: Optional[str] = None
    url: Optional[str] = None
    video_link: Optional[str] = None
    audio_link: Optional[str] = None
    cover: Optional[List[HttpUrl]] = Field(default_factory=list)
    author: Optional[str] = None
    likes: Optional[str] = None
    comments: Optional[str] = None
    shares: Optional[str] = None
    collections: Optional[str] = None
    author_id: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    release_time: Optional[str] = None
    note_id: Optional[str] = None

class XHSNoteDetailResponse(BaseModel):
    code: int
    msg: str
    data: Optional[XHSNoteContentData] = None

# === Pydantic Models for Whisper API ===
class WhisperTranscriptionResponse(BaseModel):
    text: str

# === Pydantic Models for Qwen Chat Completions API (Updated) ===
class QwenMessage(BaseModel):
    role: str
    content: str

class QwenChatCompletionRequest(BaseModel):
    model: str
    messages: List[QwenMessage]

class QwenResponseMessage(BaseModel): # Updated
    role: str
    content: str
    refusal: Optional[str] = None
    annotations: Optional[Any] = None # 具体类型未知，使用 Any
    audio: Optional[Any] = None       # 具体类型未知，使用 Any
    function_call: Optional[Any] = None # 具体类型未知，使用 Any
    tool_calls: Optional[Any] = None    # 具体类型未知，使用 Any
    reasoning_content: Optional[str] = None


class QwenChoice(BaseModel): # Updated
    index: Optional[int] = None
    message: QwenResponseMessage
    finish_reason: Optional[str] = None # 在示例中为 null，保持 Optional
    logprobs: Optional[Any] = None      # 在示例中为 null，保持 Optional


class QwenUsage(BaseModel): # Updated
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    completion_tokens_details: Optional[Any] = None # 具体类型未知，使用 Any
    prompt_tokens_details: Optional[Any] = None   # 具体类型未知，使用 Any
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None


class QwenCompletionResponse(BaseModel): # Updated
    id: Optional[str] = None
    object: Optional[str] = None
    created: Optional[int] = None
    model: Optional[str] = None
    choices: List[QwenChoice]
    usage: Optional[QwenUsage] = None
    service_tier: Optional[Any] = None # 具体类型未知，使用 Any
    system_fingerprint: Optional[Any] = None # 具体类型未知，使用 Any

# === Service Functions ===

async def get_xhs_user_posts(user_id: str, cookie: str) -> Optional[XHSUserPostResponse]:
    api_url = f"{settings.XHS_API_BASE_URL}/user/post"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.XHS_API_TOKEN}",
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)"
    }
    payload = XHSUserPostRequest(user_id=user_id, cookie=cookie).model_dump()
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(api_url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            return XHSUserPostResponse(**response.json())
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred while fetching user posts: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"An error occurred while fetching user posts: {e}")
            return None

async def get_xhs_note_detail(note_url: HttpUrl, cookie: Optional[str] = None) -> Optional[XHSNoteDetailResponse]:
    """
    获取小红书笔记详情
    
    Args:
        note_url: 小红书笔记URL (包含查询参数如xsec_token和xsec_source)
        cookie: 用户的cookie（可选）
        
    Returns:
        包含笔记详情的响应对象，请求失败时返回None
    """
    api_url = f"{settings.XHS_API_BASE_URL}/note/detail"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.XHS_API_TOKEN}",
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "Accept": "*/*"
    }
    
    # 将HttpUrl对象转换为字符串，以便正确JSON序列化
    payload = XHSNoteDetailRequest(url=str(note_url), cookie=cookie).model_dump()
    print(f"Fetching note detail from URL: {note_url}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(api_url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            return XHSNoteDetailResponse(**response.json())
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred while fetching note detail: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"An error occurred while fetching note detail: {e}")
            return None

async def transcribe_audio(file_path: str, model: str = "whisper-1") -> Optional[WhisperTranscriptionResponse]:
    api_url = f"{settings.AI_API_BASE_URL}/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {settings.AI_API_KEY}",
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)" # 统一添加User-Agent
    }
    if not os.path.exists(file_path):
        print(f"Error: Audio file not found at {file_path}")
        return None
    try:
        with open(file_path, "rb") as audio_file:
            files = {"file": (os.path.basename(file_path), audio_file, "audio/mpeg")}
            data = {"model": model}
            async with httpx.AsyncClient() as client:
                response = await client.post(api_url, headers=headers, files=files, data=data, timeout=120.0)
                response.raise_for_status()
                return WhisperTranscriptionResponse(**response.json())
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred during audio transcription: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        print(f"An error occurred during audio transcription: {e}")
        return None

async def get_qwen_chat_completion(
    messages: List[QwenMessage],
    model_name: str = "qwen3-30b-a3b" # 默认模型，可以被调用时覆盖
) -> Optional[QwenCompletionResponse]:
    api_url = f"{settings.AI_API_BASE_URL}/chat/completions"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.AI_API_KEY}",
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)" # 添加 User-Agent
    }
    payload_messages = [msg.model_dump() for msg in messages]
    payload = QwenChatCompletionRequest(model=model_name, messages=payload_messages).model_dump()
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(api_url, headers=headers, json=payload, timeout=60.0)
            response.raise_for_status()
            return QwenCompletionResponse(**response.json())
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred during Qwen chat completion: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"An error occurred during Qwen chat completion: {e}")
            return None
        
# TDOO 完善两个qwen接口