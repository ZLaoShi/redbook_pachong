from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import Column, DateTime, func
from typing import Any

@as_declarative()
class Base:
    """
    Base class which provides automated table name
    and surrogate primary key column.
    """
    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s" # 例如 User -> users, Task -> tasks

    # 默认添加 created_at 和 updated_at 字段
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
