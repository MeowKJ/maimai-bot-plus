# my_database_lib/crud.py

from .models import session, User
from .base62_utils import encode_base62, decode_base62
from .exceptions import UserNotFoundError, DatabaseOperationError

# 设置日志配置
from botpy import logger


def add_or_update_user(id_number: int, name: str, paltform_id: int):
    logger.info(f"[Database] id:[{id}] name[{name}] platform_id[{paltform_id}]")
    id_base62 = encode_base62(id_number)
    try:
        # 查找是否已有该用户
        user = session.query(User).filter(User.id == id_base62).first()
        if user:
            # 用户存在，更新名字
            user.name = name

            # 用户存在，更新平台
            user.paltform_id = paltform_id

            session.commit()
            logger.info(f"[Database] User with ID {id_base62} name updated to {name}.")
        else:
            # 用户不存在，创建新用户
            new_user = User(id=id_base62, name=name, paltform_id=paltform_id)
            session.add(new_user)
            session.commit()
            logger.info(f"[Database] User with ID {id_base62} added.")
    except Exception as e:
        logger.error(
            f"[Database] Error adding or updating user with ID {id_base62}: {e}"
        )
        raise DatabaseOperationError(
            f"Error adding or updating user with ID {id_base62}: {e}"
        )


def update_user_favorite(id_number: int, favorite_id: int):
    id_base62 = encode_base62(id_number)
    try:
        user = session.query(User).filter(User.id == id_base62).first()
        if user:
            user.favorite_id = favorite_id
            session.commit()
            logger.info(
                f"[Database] User with ID {id_base62} favorite updated to {favorite_id}."
            )
        else:
            logger.warning(f"[Database] User with ID {id_base62} not found.")
            raise UserNotFoundError(f"User with ID {id_base62} not found.")
    except Exception as e:
        logger.error(
            f"[Database] Error updating favorite for user with ID {id_base62}: {e}"
        )
        raise DatabaseOperationError(
            f"Error updating favorite for user with ID {id_base62}: {e}"
        )


def get_user_by_id(id_number: int):
    id_base62 = encode_base62(id_number)
    try:
        user = session.query(User).filter(User.id == id_base62).first()
        if user:
            return user.name, user.paltform_id, user.score, user.favorite_id
        else:
            logger.warning(f"[Database] User with ID {id_base62} not found.")
            raise UserNotFoundError(f"User with ID {id_base62} not found.")
    except Exception as e:
        logger.error(f"[Database] Error retrieving user with ID {id_base62}: {e}")
        raise DatabaseOperationError(f"Error retrieving user with ID {id_base62}: {e}")


def update_user_score(id_number: int, new_score: int):
    id_base62 = encode_base62(id_number)
    try:
        user = session.query(User).filter(User.id == id_base62).first()
        if user:
            user.score = new_score
            user.score_update_count += 1  # 每次操作将 score_update_count 加 1
            session.commit()
            logger.info(
                f"[Database] User with ID {id_base62} score updated to {new_score}, "
                f"score_update_count incremented to {user.score_update_count}."
            )
        else:
            logger.warning(f"[Database] User with ID {id_base62} not found.")
            raise UserNotFoundError(f"User with ID {id_base62} not found.")
    except Exception as e:
        logger.error(
            f"[Database] Error updating score for user with ID {id_base62}: {e}"
        )
        raise DatabaseOperationError(
            f"Error updating score for user with ID {id_base62}: {e}"
        )


def update_user_data(id_number: int, data: str):
    id_base62 = encode_base62(id_number)
    try:
        user = session.query(User).filter(User.id == id_base62).first()
        if user:
            user.data = data
            session.commit()
            logger.info(f"[Database] User with ID {id_base62} data updated to {data}.")
        else:
            logger.warning(f"[Database] User with ID {id_base62} not found.")
            raise UserNotFoundError(f"User with ID {id_base62} not found.")
    except Exception as e:
        logger.error(
            f"[Database] Error updating data for user with ID {id_base62}: {e}"
        )
        raise DatabaseOperationError(
            f"Error updating data for user with ID {id_base62}: {e}"
        )


def delete_user(id_number: int):
    id_base62 = encode_base62(id_number)
    try:
        user = session.query(User).filter(User.id == id_base62).first()
        if user:
            session.delete(user)
            session.commit()
            logger.info(f"[Database] User with ID {id_base62} deleted.")
        else:
            logger.warning(f"[Database] User with ID {id_base62} not found.")
            raise UserNotFoundError(f"User with ID {id_base62} not found.")
    except Exception as e:
        logger.error(f"[Database] Error deleting user with ID {id_base62}: {e}")
        raise DatabaseOperationError(f"Error deleting user with ID {id_base62}: {e}")
