import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载 .env 文件 (如果存在)
# 在 Docker 环境中，我们通常直接通过 docker-compose.yml 设置环境变量
load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"

    # 数据库配置
    # DATABASE_URL 会从环境变量中读取 (见 docker-compose.yml)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@host:port/db")

    # JWT Token 配置 (用于用户认证)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "a_very_secret_key_that_should_be_changed")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # 小红书 API (如果需要全局配置)
    XHS_API_BASE_URL: str = "https://aihubmax.com/ability/collect/xhs"
    XHS_API_TOKEN: str = os.getenv("XHS_API_TOKEN", "sk-1jj0WJyWJl2V4n2P50dq5xfgUQfEKa5a5Bsro81vmMTbY4hq") # 示例Token，应从环境变量获取

    # AI 模型 API (如果需要全局配置)
    AI_API_BASE_URL: str = "https://aihubmax.com/v1"
    AI_API_KEY: str = os.getenv("AI_API_KEY", "your_ai_api_key_here") # 示例Key，应从环境变量获取

    # 定时任务配置
    BACKGROUND_TASK_INTERVAL_SECONDS: int = 15

    class Config:
        case_sensitive = True
        # env_file = ".env" # 如果你想从 .env 文件加载

settings = Settings()