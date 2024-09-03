# my_database_lib/models.py

from sqlalchemy import create_engine, Column, String, Integer, DateTime, SmallInteger
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from config import DATABASE_PATH

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    data = Column(String(255), nullable=True)
    platform_id = Column(SmallInteger, default=0)
    score = Column(Integer, default=0)
    score_update_count = Column(Integer, default=0)
    favorite_id = Column(SmallInteger, default=0)
    modified_at = Column(
        DateTime,
        default=lambda: datetime.now(),
        onupdate=lambda: datetime.now(),
    )


# 创建SQLite数据库引擎
# engine = create_engine("", echo=True)
engine = create_engine(f"sqlite:///{DATABASE_PATH}")

# 创建表格
Base.metadata.create_all(engine)

# 创建Session类
# Session = sessionmaker(bind=engine)
# session = Session()
