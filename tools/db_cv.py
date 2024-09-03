import sqlite3
import uuid
from sqlalchemy import create_engine, Column, Integer, String, SmallInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import string

# 定义 Base62 解码函数
BASE62_ALPHABET = string.ascii_letters + string.digits
BASE62_ALPHABET_MAP = {char: index for index, char in enumerate(BASE62_ALPHABET)}
BASE62_BASE = len(BASE62_ALPHABET)


def decode_base62(base62_string: str) -> int:
    number = 0
    for char in base62_string:
        number = number * BASE62_BASE + BASE62_ALPHABET_MAP[char]
    print(f"[Database] Decoded Base62 string {base62_string} to number {number}.")
    return number


# 定义新的数据库模型
Base = declarative_base()


class NewUser(Base):
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
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
    )


# 创建新的数据库连接
new_engine = create_engine("sqlite:///new_database.db")
Base.metadata.create_all(new_engine)
NewSession = sessionmaker(bind=new_engine)
new_session = NewSession()

# 连接旧的数据库
old_conn = sqlite3.connect("local.db")
old_cursor = old_conn.cursor()

# 查询旧数据库中的用户数据
old_cursor.execute(
    "SELECT id, name, paltform_id, data, score, score_update_count, favorite_id, modified_at FROM users"
)
old_users = old_cursor.fetchall()

# 迁移数据到新的数据库
for old_user in old_users:
    # 解码旧的 Base62 ID
    decoded_id = decode_base62(old_user[0])

    # 使用解码后的 ID 生成新的 36 位 user_id
    new_user_id = str(decoded_id)

    # 创建新的用户实例
    new_user = NewUser(
        user_id=new_user_id,
        name=old_user[1],
        platform_id=old_user[2],
        data=old_user[3],
        score=old_user[4],
        score_update_count=old_user[5],
        favorite_id=old_user[6],
        modified_at=datetime.datetime.now(datetime.timezone.utc),
    )

    # 将新用户添加到新数据库会话中
    new_session.add(new_user)

# 提交会话并关闭
new_session.commit()
new_session.close()

# 关闭旧数据库连接
old_conn.close()

print("数据迁移完成。")
