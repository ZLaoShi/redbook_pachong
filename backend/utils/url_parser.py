import re
from typing import Optional

def extract_blogger_id_from_url(url: str) -> Optional[str]:
    """
    从小红书博主个人主页URL中提取博主ID
    
    示例URL:
    - https://www.xiaohongshu.com/user/profile/5a0a2f7fe8ac2b7abfb21ead
    - https://xiaohongshu.com/user/profile/632d1a99000000002303cc9d
    
    返回: 博主ID (如 5a0a2f7fe8ac2b7abfb21ead)
    """
    match = re.search(r"/user/profile/([^/?&#]+)", str(url))
    if match:
        return match.group(1)
    return None

def extract_note_id_from_url(url: str) -> Optional[str]:
    """
    从小红书笔记URL中提取笔记ID
    
    示例URL:
    - https://www.xiaohongshu.com/explore/645b6a19000000001301485a
    - https://xiaohongshu.com/explore/676a13550000000013009b28
    
    返回: 笔记ID (如 645b6a19000000001301485a)
    """
    match = re.search(r"/explore/([^/?&#]+)", str(url))
    if match:
        return match.group(1)
    return None

def construct_note_url(note_id: str) -> str:
    """
    根据笔记ID构建完整的笔记URL
    """
    return f"https://www.xiaohongshu.com/explore/{note_id}"

def construct_blogger_url(blogger_id: str) -> str:
    """
    根据博主ID构建完整的博主主页URL
    """
    return f"https://www.xiaohongshu.com/user/profile/{blogger_id}"