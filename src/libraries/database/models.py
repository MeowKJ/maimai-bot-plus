# my_database_lib/models.py

from sqlalchemy import create_engine, Column, String, Integer, DateTime, SmallInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(String(16), primary_key=True)
    name = Column(String(255), nullable=False)
    paltform_id = Column(SmallInteger, nullable=False)
    data = Column(String(255), nullable=True)
    score = Column(Integer, default=0)
    score_update_count = Column(Integer, default=0)
    favorite_id = Column(SmallInteger, default=0)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# 创建SQLite数据库引擎
engine = create_engine("sqlite:///local.db", echo=True)

# 创建表格
Base.metadata.create_all(engine)

# 创建Session类
Session = sessionmaker(bind=engine)
session = Session()
