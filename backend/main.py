import asyncio
from fastapi import FastAPI
import uvicorn
from concurrent.futures import ThreadPoolExecutor

# 导入数据库相关
from db.database import engine
from db.base_class import Base
# 导入所有模型，以便 Base 能找到它们来创建表
from models import User, Task, Note

from api.v1.api import api_router as api_v1_router
from core.config import settings
from worker.task_processor import run_background_tasks

# 在应用启动前创建数据库表 (仅用于开发)
def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="小红书笔记分析工具 API",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 用于运行后台任务的executor
background_tasks_executor = ThreadPoolExecutor(max_workers=1)
background_task = None

@app.on_event("startup")
async def on_startup():
    # 创建数据库表
    create_db_and_tables()
    print("Database tables created (if they didn't exist).")
    
    # 启动后台任务
    global background_task
    loop = asyncio.get_event_loop()
    background_task = loop.run_in_executor(background_tasks_executor, asyncio.run, run_background_tasks())
    print("Background tasks started.")

@app.on_event("shutdown")
async def on_shutdown():
    # 关闭后台任务
    global background_task
    if background_task:
        background_tasks_executor.shutdown(wait=False)
        print("Background tasks stopped.")

# 包含 v1 版本的 API 路由
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "欢迎使用小红书笔记分析工具 API. 请访问 /api/v1/docs 查看 API 文档。"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)