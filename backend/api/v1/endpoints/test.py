from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional, List

from services.aihubmax_service import (
    get_xhs_user_posts, 
    get_xhs_note_detail,
    XHSUserPostResponse, 
    XHSNoteDetailResponse
)
from services.enhanced_xhs_service import get_enhanced_note_detail
from services.xhs_client import XHSClient
from api import deps

router = APIRouter()

class UserPostsRequest(BaseModel):
    user_id: str
    cookie: str

class NoteDetailRequest(BaseModel):
    url: HttpUrl
    cookie: Optional[str] = None

class EnhancedNoteDetailRequest(BaseModel):
    note_id: str
    title: str
    user_id: Optional[str] = None
    cookie: str

@router.post("/xhs_user_posts", response_model=XHSUserPostResponse)
async def test_xhs_user_posts(
    request: UserPostsRequest,
    current_user = Depends(deps.get_current_active_user)
):
    """测试小红书用户笔记列表API"""
    response = await get_xhs_user_posts(request.user_id, request.cookie)
    if not response:
        raise HTTPException(status_code=500, detail="Failed to fetch user posts")
    return response

@router.post("/xhs_note_detail", response_model=XHSNoteDetailResponse)
async def test_xhs_note_detail(
    request: NoteDetailRequest,
    current_user = Depends(deps.get_current_active_user)
):
    """测试小红书笔记详情API"""
    response = await get_xhs_note_detail(request.url, request.cookie)
    if not response:
        raise HTTPException(status_code=500, detail="Failed to fetch note detail")
    return response

@router.post("/xhs_search_notes")
async def test_search_notes(
    keyword: str,
    cookie: str,
    page: int = 1,
    page_size: int = 20,
    current_user = Depends(deps.get_current_active_user)
):
    """测试小红书搜索功能"""
    client = XHSClient(cookie)
    search_results = await client.search_notes(keyword, page, page_size)
    
    # 格式化笔记列表以便更易于查看
    formatted_results = []
    for item in search_results.get("items", []):
        if "note_card" in item:
            note_card = item["note_card"]
            user = note_card.get("user", {})
            formatted_results.append({
                "note_id": note_card.get("id", ""),
                "title": note_card.get("display_title", ""),
                "user_id": user.get("user_id", ""),
                "nickname": user.get("nickname", ""),
                "xsec_token": item.get("xsec_token", ""),
                "xsec_source": item.get("xsec_source", "pc_search")
            })
    
    return {
        "total": len(formatted_results),
        "items": formatted_results
    }


@router.post("/xhs_enhanced_note_detail", response_model=XHSNoteDetailResponse)
async def test_enhanced_note_detail(
    request: EnhancedNoteDetailRequest,
    current_user = Depends(deps.get_current_active_user)
):
    """
    增强版小红书笔记详情API：
    1. 使用标题搜索笔记（多页搜索）
    2. 从搜索结果中匹配note_id和user_id
    3. 构建完整URL
    4. 获取笔记详情
    """
    response = await get_enhanced_note_detail(
        note_id=request.note_id,
        title=request.title,
        user_id=request.user_id,
        cookie=request.cookie,
    )
    
    if not response:
        raise HTTPException(status_code=404, detail="未找到匹配的笔记或获取笔记详情失败")
    
    return response