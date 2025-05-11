from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from core.config import settings # 确保路径正确，如果 backend 是根，则 from core.config import settings

# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db" # 如果使用 SQLite
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # connect_args={"check_same_thread": False} # 仅 SQLite 需要
    pool_pre_ping=True # 检查连接有效性
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base() # 我们将使用 db.base_class.Base