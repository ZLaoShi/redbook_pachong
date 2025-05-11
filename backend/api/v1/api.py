from fastapi import APIRouter

from .endpoints import login, users, tasks, test # 导入端点模块中的 router

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"]) # 登录相关的路由
api_router.include_router(users.router, prefix="/users", tags=["users"]) # 用户相关的路由，前缀为 /users
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(test.router, prefix="/test", tags=["test"])  # 添加测试路由