from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional, List

from services.aihubmax_service import (
    get_xhs_user_posts, 
    get_xhs_note_detail,
    XHSUserPostResponse, 
    XHSNoteDetailResponse
)
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
    print(f"正在查找笔记: ID={request.note_id}, 标题={request.title}, 用户ID={request.user_id or '未提供'}")
    
    # 初始化XHSClient进行搜索
    client = XHSClient(request.cookie)
    
    # 1. 使用标题进行多页搜索
    print(f"搜索标题: {request.title}")
    # 先搜索获取所有项
    all_items = await client.search_notes_multi_page(request.title, max_pages=3, page_size=20)
    
    # 打印搜索结果概况
    print(f"搜索到 {len(all_items)} 条结果")
    for idx, item in enumerate(all_items[:10]):  # 只打印前10条避免日志过长
        if "note_card" in item:
            note_card = item["note_card"]
            print(f"结果 #{idx+1}: ID={note_card.get('id', 'N/A')}, 标题={note_card.get('display_title', 'N/A')}, 用户ID={note_card.get('user', {}).get('user_id', 'N/A')}")
    
    if not all_items:
        raise HTTPException(status_code=404, detail="未找到任何相关笔记")
    
    # 2. 筛选匹配的笔记
    matched_note = None
    
    # 首先按ID精确匹配
    for item in all_items:
        if "note_card" not in item:
            continue
            
        note_card = item["note_card"]
        current_id = note_card.get("id")
        current_user_id = note_card.get("user", {}).get("user_id")
        
        if current_id == request.note_id:
            print(f"找到ID匹配的笔记: {current_id}")
            
            # 如果提供了用户ID，也检查用户ID是否匹配
            if request.user_id and current_user_id != request.user_id:
                print(f"笔记ID匹配但用户ID不匹配: 期望={request.user_id}, 实际={current_user_id}")
                continue
            
            # 获取xsec_token
            xsec_token = item.get("xsec_token", "")
            if not xsec_token:
                print(f"笔记 {current_id} 没有xsec_token，跳过")
                continue
                
            matched_note = {
                "note_id": request.note_id,
                "xsec_token": xsec_token,
                "xsec_source": item.get("xsec_source", "pc_search"),
                "title": note_card.get("display_title", ""),
                "user_id": current_user_id
            }
            break
    
    # 如果没有通过ID找到匹配，尝试通过标题和用户ID匹配
    if not matched_note:
        print("通过ID未找到匹配笔记，尝试通过标题和用户ID匹配")
        for item in all_items:
            if "note_card" not in item:
                continue
                
            note_card = item["note_card"]
            current_title = note_card.get("display_title", "")
            current_user_id = note_card.get("user", {}).get("user_id")
            
            # 标题相似度匹配 (简化版 - 标题包含关系)
            title_match = (
                request.title.lower() in current_title.lower() or 
                current_title.lower() in request.title.lower()
            )
            user_match = not request.user_id or current_user_id == request.user_id
            
            if title_match and user_match:
                print(f"找到标题和用户ID匹配的笔记: ID={note_card.get('id')}, 标题={current_title}")
                xsec_token = item.get("xsec_token", "")
                if not xsec_token:
                    continue
                    
                matched_note = {
                    "note_id": request.note_id,  # 使用请求中的原始note_id
                    "xsec_token": xsec_token,
                    "xsec_source": item.get("xsec_source", "pc_search"),
                    "title": current_title,
                    "user_id": current_user_id
                }
                break
    
    if not matched_note:
        raise HTTPException(status_code=404, detail="未找到匹配的笔记，请检查笔记ID、标题或用户ID")
    
    print(f"找到匹配笔记: ID={matched_note['note_id']}, 用户ID={matched_note['user_id']}, 标题={matched_note['title']}")

    # 3. 构建完整URL
    full_url = client.build_note_url_with_token(
        matched_note["note_id"], 
        matched_note["xsec_token"], 
        matched_note["xsec_source"]
    )
    
    print(f"找到匹配笔记，URL: {full_url}")
    
    # 4. 获取笔记详情
    response = await get_xhs_note_detail(HttpUrl(full_url), request.cookie)
    if not response:
        raise HTTPException(status_code=500, detail="获取笔记详情失败")
    
    return response