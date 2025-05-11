import json
import logging
import re
import uuid
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode

import httpx

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class XHSClient:
    """小红书客户端，使用cookie执行API请求，无需复杂的签名"""
    
    def __init__(self, cookie_str: str = None):
        self.cookie_str = cookie_str
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Origin": "https://www.xiaohongshu.com",
            "Referer": "https://www.xiaohongshu.com/",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Content-Type": "application/json"
        }
        
        if cookie_str:
            self.headers["Cookie"] = cookie_str
            
        self._host = "https://edith.xiaohongshu.com"
        self._domain = "https://www.xiaohongshu.com"
    
    async def search_notes(self, keyword: str, page: int = 1, page_size: int = 20) -> Dict:
        """
        搜索笔记
        Args:
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量
        Returns:
            搜索结果
        """
        url = f"{self._host}/api/sns/web/v1/search/notes"
        search_id = str(uuid.uuid4())
        
        data = {
            "keyword": keyword,
            "page": page,
            "page_size": page_size,
            "search_id": search_id,
            "sort": "general",
            "note_type": 0
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url=url,
                    headers=self.headers,
                    json=data,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    logger.error(f"搜索笔记失败: {response.status_code} - {response.text}")
                    return {"items": []}
                
                result = response.json()
                if not result.get("success", False):
                    error_msg = result.get("msg", "Unknown error")
                    logger.error(f"API返回错误: {error_msg}")
                    return {"items": []}
                    
                return result.get("data", {"items": []})
                
        except Exception as e:
            logger.error(f"搜索笔记失败: {e}")
            return {"items": []}
    
    async def get_note_detail(self, note_id: str, xsec_token: str, xsec_source: str = "pc_search") -> Dict:
        """
        获取笔记详情 - 此实现仅为接口保持完整性，实际获取详情应使用外部服务
        Args:
            note_id: 笔记ID
            xsec_token: 安全令牌
            xsec_source: 来源
        Returns:
            空字典 - 因为实际调用将使用aihubmax_service
        """
        logger.info(f"获取笔记详情请求: note_id={note_id}, xsec_token={xsec_token}")
        return {}
    
    async def find_note_by_id(self, note_id: str, title: str = None) -> Dict:
        """
        通过ID搜索笔记并获取xsec_token
        Args:
            note_id: 笔记ID
            title: 笔记标题(用于搜索)
        Returns:
            包含xsec_token的笔记信息
        """
        # 如果没有提供标题，使用ID作为搜索关键词
        search_keyword = title if title else note_id
        
        try:
            # 搜索笔记
            search_results = await self.search_notes(search_keyword)
            
            # 从搜索结果中找到匹配的笔记
            for item in search_results.get("items", []):
                if "note_card" in item and item["note_card"].get("id") == note_id:
                    note_card = item["note_card"]
                    # 提取xsec_token
                    xsec_token = item.get("xsec_token", "")
                    return {
                        "note_id": note_id,
                        "xsec_token": xsec_token,
                        "xsec_source": item.get("xsec_source", "pc_search"),
                        "title": note_card.get("display_title", ""),
                        "user_id": note_card.get("user", {}).get("user_id", ""),
                        "nickname": note_card.get("user", {}).get("nickname", "")
                    }
            
            # 如果没有找到匹配的笔记，尝试使用note_id直接搜索
            if title:
                return await self.find_note_by_id(note_id)
                
            logger.error(f"未找到笔记: {note_id}")
            return {}
            
        except Exception as e:
            logger.error(f"查找笔记失败: {e}")
            return {}

    async def find_notes_by_keyword(self, keyword: str, limit: int = 20) -> List[Dict]:
        """
        搜索笔记并返回格式化后的结果列表
        Args:
            keyword: 搜索关键词
            limit: 返回数量限制
        Returns:
            包含笔记基本信息的列表
        """
        try:
            search_results = await self.search_notes(keyword, page=1, page_size=limit)
            notes_list = []
            
            for item in search_results.get("items", []):
                if "note_card" in item:
                    note_card = item["note_card"]
                    user = note_card.get("user", {})
                    
                    notes_list.append({
                        "note_id": note_card.get("id", ""),
                        "title": note_card.get("display_title", ""),
                        "desc": note_card.get("desc", ""),
                        "type": note_card.get("type", ""),
                        "user_id": user.get("user_id", ""),
                        "nickname": user.get("nickname", ""),
                        "xsec_token": item.get("xsec_token", ""),
                        "xsec_source": item.get("xsec_source", "pc_search"),
                        "url": f"{self._domain}/explore/{note_card.get('id', '')}"
                    })
            
            return notes_list
        
        except Exception as e:
            logger.error(f"关键词搜索笔记失败: {e}")
            return []

    def build_note_url_with_token(self, note_id: str, xsec_token: str, xsec_source: str = "pc_search") -> str:
        """
        构建包含安全令牌的笔记URL
        Args:
            note_id: 笔记ID
            xsec_token: 安全令牌
            xsec_source: 来源
        Returns:
            完整的带令牌的URL
        """
        return f"{self._domain}/explore/{note_id}?xsec_token={xsec_token}&xsec_source={xsec_source}"

    @classmethod
    def parse_note_info_from_url(cls, url: str) -> Dict:
        """
        从小红书笔记url中解析出笔记信息
        Args:
            url: "https://www.xiaohongshu.com/explore/66fad51c000000001b0224b8?xsec_token=..."
        Returns:
            包含note_id、xsec_token等信息的字典
        """
        # 解析URL获取note_id
        match = re.search(r"/explore/([^/?]+)", url)
        if not match:
            return {}
            
        note_id = match.group(1)
        
        # 解析查询参数
        params = {}
        query_string = url.split("?", 1)[1] if "?" in url else ""
        if query_string:
            for pair in query_string.split("&"):
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    params[key] = value
        
        return {
            "note_id": note_id,
            "xsec_token": params.get("xsec_token", ""),
            "xsec_source": params.get("xsec_source", "pc_search")
        }

    async def search_notes_multi_page(self, keyword: str, max_pages: int = 5, page_size: int = 20) -> List[Dict]:
        """
        多页搜索笔记，自动翻页直到找到结果或达到最大页数
        Args:
            keyword: 搜索关键词
            max_pages: 最大搜索页数
            page_size: 每页数量
        Returns:
            所有页面的笔记列表合并结果
        """
        all_items = []
        
        for page in range(1, max_pages + 1):
            logger.info(f"搜索关键词 '{keyword}' 第 {page} 页")
            search_results = await self.search_notes(keyword, page=page, page_size=page_size)
            items = search_results.get("items", [])
            
            if not items:
                logger.info(f"第 {page} 页没有返回结果，停止搜索")
                break
                
            all_items.extend(items)
            
            # 如果返回的结果数量小于page_size，说明没有更多页了
            if len(items) < page_size:
                logger.info(f"第 {page} 页返回结果数量（{len(items)}）小于请求数量（{page_size}），没有更多页")
                break
                
        return all_items