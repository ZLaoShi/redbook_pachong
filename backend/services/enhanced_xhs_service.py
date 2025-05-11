import logging
import asyncio
from typing import Dict, Optional, Tuple, List, Any, Callable
from pydantic import HttpUrl
from enum import Enum

from services.xhs_client import XHSClient
from services.aihubmax_service import get_xhs_note_detail, XHSNoteDetailResponse

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchSortType(str, Enum):
    GENERAL = "general"  # 综合排序
    LIKES = "likes_desc"  # 按点赞数倒序
    TIME_DESC = "time_desc"  # 按时间倒序
    TIME_ASC = "time_asc"  # 按时间升序

class NoteType(str, Enum):
    ALL = 0  # 所有类型
    VIDEO = 1  # 视频
    IMAGE = 2  # 图文

async def search_notes_until_end(
    client: XHSClient,
    keyword: str,
    max_pages: int = 10,  # 增加最大页数上限
    page_size: int = 20,
    sort_type: SearchSortType = SearchSortType.GENERAL,
    note_type: NoteType = NoteType.ALL
) -> List[Dict]:
    """
    一直搜索直到最后一页或达到最大页数限制
    
    Args:
        client: XHSClient实例
        keyword: 搜索关键词
        max_pages: 最大搜索页数
        page_size: 每页大小
        sort_type: 搜索结果排序方式
        note_type: 笔记类型筛选
        
    Returns:
        所有搜索结果列表
    """
    all_items = []
    has_more = True
    
    for page in range(1, max_pages + 1):
        if not has_more:
            break
            
        logger.info(f"搜索关键词 '{keyword}' 第 {page}/{max_pages} 页 (排序: {sort_type}, 类型: {note_type})")
        
        try:
            # 使用带排序和类型筛选的搜索
            search_data = {
                "keyword": keyword,
                "page": page,
                "page_size": page_size,
                "sort": sort_type,
                "note_type": note_type
            }
            
            search_results = await client.search_notes_with_options(search_data)
            items = search_results.get("items", [])
            
            # 检查是否到最后一页
            if not items:
                logger.info(f"第 {page} 页没有返回结果，搜索结束")
                has_more = False
                break
                
            all_items.extend(items)
                
            # 如果返回的结果数量小于page_size，说明没有更多页了
            if len(items) < page_size:
                logger.info(f"第 {page} 页返回结果数量（{len(items)}）小于请求数量（{page_size}），搜索结束")
                has_more = False
                
        except Exception as e:
            logger.error(f"搜索第 {page} 页时发生错误: {e}")
            break
            
    logger.info(f"共搜索到 {len(all_items)} 条结果")
    return all_items

async def find_note_with_token_basic(
    client: XHSClient,
    note_id: str,
    title: str,
    user_id: Optional[str] = None,
    search_options: Optional[Dict] = None
) -> Optional[Dict]:
    """
    基础搜索策略：使用标题搜索，选择第一个有token的结果
    
    Args:
        client: XHSClient实例
        note_id: 笔记ID
        title: 笔记标题
        user_id: 用户ID (可选)
        search_options: 搜索选项
        
    Returns:
        匹配的笔记或None
    """
    options = search_options or {}
    max_pages = options.get("max_pages", 10)
    page_size = options.get("page_size", 20)
    sort_type = options.get("sort_type", SearchSortType.GENERAL)
    note_type = options.get("note_type", NoteType.ALL)
    
    # 执行搜索
    all_items = await search_notes_until_end(
        client, title, max_pages, page_size, sort_type, note_type
    )
    
    # 找第一个匹配的结果
    for item in all_items:
        if "note_card" not in item or not item.get("xsec_token"):
            continue
            
        note_card = item["note_card"]
        current_id = note_card.get("id")
        current_user_id = note_card.get("user", {}).get("user_id")
        current_title = note_card.get("display_title", "")
        
        # 检查用户ID匹配(如果提供了用户ID)
        if user_id and current_user_id != user_id:
            logger.debug(f"跳过不匹配的用户ID: 笔记ID={current_id}, 期望用户ID={user_id}, 实际用户ID={current_user_id}")
            continue
            
        # 获取xsec_token
        xsec_token = item.get("xsec_token", "")
        if not xsec_token:
            logger.debug(f"笔记 {current_id} 没有xsec_token，跳过")
            continue
            
        # 找到匹配的笔记
        matched_note = {
            "note_id": note_id,  # 保留原始note_id，而不是使用搜索结果中的ID
            "found_id": current_id,  # 记录找到的ID，以便调试
            "xsec_token": xsec_token,
            "xsec_source": item.get("xsec_source", "pc_search"),
            "title": current_title,
            "user_id": current_user_id
        }
        logger.info(f"找到匹配笔记: 原始ID={note_id}, 搜索ID={current_id}, 标题=\"{current_title}\"")
        return matched_note
        
    logger.warning(f"使用基础策略未找到匹配的笔记")
    return None

async def find_note_with_token_by_title_words(
    client: XHSClient,
    note_id: str,
    title: str,
    user_id: Optional[str] = None,
    search_options: Optional[Dict] = None
) -> Optional[Dict]:
    """
    关键词策略：拆分标题为关键词，分别搜索
    
    Args:
        client: XHSClient实例
        note_id: 笔记ID
        title: 笔记标题
        user_id: 用户ID (可选)
        search_options: 搜索选项
        
    Returns:
        匹配的笔记或None
    """
    if not title or len(title) < 3:
        return None
        
    # 将标题拆分为关键词
    words = title.split()
    keywords = []
    
    # 提取长度大于1的词
    for word in words:
        if len(word) > 1:
            keywords.append(word)
            
    # 如果提取不到关键词，直接返回None
    if not keywords:
        return None
        
    logger.info(f"从标题 '{title}' 提取关键词: {keywords}")
    
    # 逐个尝试关键词
    for keyword in keywords:
        logger.info(f"使用关键词搜索: '{keyword}'")
        
        # 使用基础搜索函数
        matched_note = await find_note_with_token_basic(
            client, note_id, keyword, user_id, search_options
        )
        
        if matched_note:
            return matched_note
            
    logger.warning(f"使用关键词策略未找到匹配的笔记")
    return None

async def find_note_with_token(
    note_id: str, 
    title: str, 
    user_id: Optional[str] = None, 
    cookie: str = None,
    max_pages: int = 10,
    page_size: int = 20,
    search_config: Optional[Dict] = None
) -> Optional[Dict]:
    """
    查找笔记并获取xsec_token - 统一入口函数
    
    Args:
        note_id: 笔记ID
        title: 笔记标题
        user_id: 用户ID (可选)
        cookie: 用户cookie
        max_pages: 最大搜索页数
        page_size: 每页大小
        search_config: 额外搜索配置
        
    Returns:
        包含note_id, xsec_token等的匹配结果，未找到则返回None
    """
    logger.info(f"正在查找笔记: ID={note_id}, 标题={title}, 用户ID={user_id or '未提供'}")
    
    # 初始化XHSClient
    client = XHSClient(cookie)
    
    # 配置搜索选项
    config = search_config or {}
    search_options = {
        "max_pages": max_pages,
        "page_size": page_size,
        "sort_type": config.get("sort_type", SearchSortType.GENERAL),
        "note_type": config.get("note_type", NoteType.ALL)
    }
    
    # 搜索策略1: 使用完整标题搜索
    logger.info("策略1: 使用完整标题搜索")
    matched_note = await find_note_with_token_basic(
        client, note_id, title, user_id, search_options
    )
    if matched_note:
        return matched_note
        
    # 搜索策略2: 使用分词搜索
    logger.info("策略2: 使用标题分词搜索")
    matched_note = await find_note_with_token_by_title_words(
        client, note_id, title, user_id, search_options
    )
    if matched_note:
        return matched_note
        
    # 搜索策略3: 使用排序方式搜索
    logger.info("策略3: 按点赞数排序搜索")
    likes_options = search_options.copy()
    likes_options["sort_type"] = SearchSortType.LIKES
    matched_note = await find_note_with_token_basic(
        client, note_id, title, user_id, likes_options
    )
    if matched_note:
        return matched_note
        
    # 所有策略都失败
    logger.warning(f"所有搜索策略均未找到笔记: ID={note_id}, 标题={title}")
    return None

async def get_enhanced_note_detail_with_retry(
    note_id: str, 
    title: str, 
    user_id: Optional[str] = None, 
    cookie: str = None,
    max_retries: int = 3,
    retry_delay: float = 3.0,
    search_retries: int = 2,
    search_config: Optional[Dict] = None
) -> Optional[XHSNoteDetailResponse]:
    """
    带重试机制的增强版笔记详情获取函数
    
    Args:
        note_id: 笔记ID
        title: 笔记标题
        user_id: 用户ID (可选)
        cookie: 用户cookie
        max_retries: 获取详情的最大重试次数
        retry_delay: 重试之间的延迟(秒)
        search_retries: 搜索匹配笔记的重试次数
        search_config: 搜索配置选项
        
    Returns:
        笔记详情响应或None
    """
    matched_note = None
    
    # 1. 尝试查找笔记并获取xsec_token (带重试)
    for search_attempt in range(search_retries):
        try:
            # 每次重试使用不同的搜索配置
            current_config = search_config or {}
            
            # 根据重试次数调整搜索策略
            if search_attempt == 1:
                # 第二次尝试使用点赞排序
                current_config["sort_type"] = SearchSortType.LIKES
            elif search_attempt == 2:
                # 第三次尝试限定视频类型
                current_config["note_type"] = NoteType.VIDEO
                
            matched_note = await find_note_with_token(
                note_id, title, user_id, cookie, 
                search_config=current_config
            )
            
            if matched_note:
                break
                
            if search_attempt < search_retries - 1:
                logger.info(f"未找到匹配笔记，第 {search_attempt+1}/{search_retries} 次尝试失败，将在 {retry_delay} 秒后重试")
                await asyncio.sleep(retry_delay)
        except Exception as e:
            logger.error(f"查找笔记过程中发生异常: {e}")
            if search_attempt < search_retries - 1:
                logger.info(f"将在 {retry_delay} 秒后重试搜索")
                await asyncio.sleep(retry_delay)
    
    if not matched_note:
        logger.error(f"经过 {search_retries} 次尝试，仍未找到匹配的笔记, note_id={note_id}, title={title}")
        return None
    
    # 2. 构建完整URL
    client = XHSClient(cookie)
    full_url = client.build_note_url_with_token(
        matched_note["note_id"], 
        matched_note["xsec_token"], 
        matched_note["xsec_source"]
    )
    
    # 3. 获取笔记详情 (带重试)
    for attempt in range(max_retries):
        try:
            logger.info(f"获取笔记详情 (尝试 {attempt+1}/{max_retries}): {full_url}")
            response = await get_xhs_note_detail(HttpUrl(full_url), cookie)
            
            # 检查响应是否有效
            if response and response.code == 0:
                logger.info(f"成功获取笔记详情: {note_id}")
                return response
            else:
                error_msg = response.msg if response else "未知错误"
                logger.error(f"获取笔记详情API返回错误 (尝试 {attempt+1}/{max_retries}): {error_msg}")
                
                # 最后一次尝试失败，返回None
                if attempt == max_retries - 1:
                    return None
                    
                # 否则等待后重试
                logger.info(f"将在 {retry_delay} 秒后重试")
                await asyncio.sleep(retry_delay)
                
        except Exception as e:
            logger.error(f"获取笔记详情时发生异常 (尝试 {attempt+1}/{max_retries}): {e}")
            
            # 最后一次尝试失败，返回None
            if attempt == max_retries - 1:
                return None
                
            # 否则等待后重试
            logger.info(f"将在 {retry_delay} 秒后重试")
            await asyncio.sleep(retry_delay)
    
    # 所有重试都失败
    return None

# 保持原有函数名兼容性
async def get_enhanced_note_detail(
    note_id: str, 
    title: str, 
    user_id: Optional[str] = None, 
    cookie: str = None,
    note_type: Optional[str] = None  # 保留参数但不使用
) -> Optional[XHSNoteDetailResponse]:
    """
    增强版笔记详情获取函数 - 使用最简单稳定的搜索策略
    使用完整标题进行搜索，不指定任何筛选条件，搜索到最后一页
    
    Args:
        note_id: 笔记ID
        title: 笔记标题
        user_id: 用户ID (可选)
        cookie: 用户cookie
        note_type: 笔记类型 (保留但不使用)
        
    Returns:
        笔记详情响应或None
    """
    logger.info(f"使用简单搜索策略查找笔记: ID={note_id}, 标题={title}")
    
    # 初始化XHSClient
    client = XHSClient(cookie)
    
    # 执行最简单的搜索，不指定任何额外条件
    all_items = await client.search_notes_multi_page(
        keyword=title,
        max_pages=200,  # 搜索更多页提高成功率
        page_size=20
    )
    
    logger.info(f"搜索到 {len(all_items)} 条结果")
    
    # 记录所有搜索结果的基本信息
    for idx, item in enumerate(all_items):
        if "note_card" in item:
            note_card = item["note_card"]
            current_id = note_card.get("id", "N/A")
            current_title = note_card.get("display_title", "N/A")
            current_user_id = note_card.get("user", {}).get("user_id", "N/A")
            has_token = "有xsec_token" if item.get("xsec_token") else "无xsec_token"
            
            logger.info(f"结果 #{idx+1}: ID={current_id}, 标题=\"{current_title}\", 用户ID={current_user_id}, {has_token}")
    
    # 找第一个有效的结果
    matched_note = None
    for item in all_items:
        if "note_card" not in item or not item.get("xsec_token"):
            continue
        
        note_card = item["note_card"]
        current_id = note_card.get("id")
        current_user_id = note_card.get("user", {}).get("user_id")
        current_title = note_card.get("display_title", "")
        
        # 获取xsec_token
        xsec_token = item.get("xsec_token", "")
        if not xsec_token:
            continue
        
        # 找到匹配的笔记
        matched_note = {
            "note_id": note_id,  # 保留原始note_id
            "found_id": current_id,  # 记录找到的ID
            "xsec_token": xsec_token,
            "xsec_source": item.get("xsec_source", "pc_search"),
            "title": current_title,
            "user_id": current_user_id
        }
        logger.info(f"选择第一个有效结果: ID={current_id}, 标题=\"{current_title}\"")
        break
    
    if not matched_note:
        logger.error(f"未找到任何有效结果: note_id={note_id}, title={title}")
        return None
    
    # 构建完整URL
    full_url = client.build_note_url_with_token(
        matched_note["note_id"], 
        matched_note["xsec_token"], 
        matched_note["xsec_source"]
    )

     # 打印构建后的完整URL
    logger.info(f"构建的完整URL: {full_url}")
    
    # 获取笔记详情 (带重试)
    max_retries = 10
    retry_delay = 3.0
    
    for attempt in range(max_retries):
        try:
            logger.info(f"获取笔记详情 (尝试 {attempt+1}/{max_retries}): {full_url}")
            response = await get_xhs_note_detail(HttpUrl(full_url), cookie)
            
            # 检查响应是否有效
            if response and response.code == 0:
                logger.info(f"成功获取笔记详情: {note_id}")
                return response
            else:
                error_msg = response.msg if response else "未知错误"
                logger.error(f"获取笔记详情API返回错误 (尝试 {attempt+1}/{max_retries}): {error_msg}")
                
                # 最后一次尝试失败，返回None
                if attempt == max_retries - 1:
                    return None
                    
                # 否则等待后重试
                logger.info(f"将在 {retry_delay} 秒后重试")
                await asyncio.sleep(retry_delay)
                
        except Exception as e:
            logger.error(f"获取笔记详情时发生异常 (尝试 {attempt+1}/{max_retries}): {e}")
            
            # 最后一次尝试失败，返回None
            if attempt == max_retries - 1:
                return None
                
            # 否则等待后重试
            logger.info(f"将在 {retry_delay} 秒后重试")
            await asyncio.sleep(retry_delay)
    
    # 所有重试都失败
    return None
# TODO: 逆向小红书的属性搜索，应用优化策略
# TODO: 实现根据用户任务行为创建策略