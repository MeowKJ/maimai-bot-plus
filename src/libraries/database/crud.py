import logging
from typing import Tuple, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from botpy import logger


# Assume these modules exist in your project
from .models import User
from .exceptions import UserNotFoundError, DatabaseOperationError

from config import DATABASE_PATH

# Database configuration

# Create the engine and configure session factory
engine = create_engine(f"sqlite:///{DATABASE_PATH}")

# Create a thread-safe scoped session
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

# Global session object
session: Session = SessionLocal()


def add_or_update_user(user_id: str, name: str, platform_id: int) -> None:
    """
    添加或更新用户信息。如果用户已存在，则更新用户的名字和平台 ID，否则创建新用户。
    """
    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            user.name = name
            user.platform_id = platform_id
        else:
            new_user = User(user_id=user_id, name=name, platform_id=platform_id)
            session.add(new_user)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"[Database] Error adding or updating user with ID {user_id}: {e}")
        raise DatabaseOperationError(
            f"Error adding or updating user with ID {user_id}: {e}"
        )


def update_user_favorite(user_id: str, favorite_id: int) -> None:
    """
    更新用户的收藏夹 ID。
    """
    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            user.favorite_id = favorite_id
            session.commit()
            logger.info(
                f"[Database] User with ID {user_id} favorite updated to {favorite_id}."
            )
        else:
            logger.warning(f"[Database] User with ID {user_id} not found.")
            raise UserNotFoundError(f"User with ID {user_id} not found.")
    except Exception as e:
        session.rollback()
        logger.error(
            f"[Database] Error updating favorite for user with ID {user_id}: {e}"
        )
        raise DatabaseOperationError(
            f"Error updating favorite for user with ID {user_id}: {e}"
        )


def get_user_by_id(user_id: str) -> Tuple[str, int, int, int]:
    """
    根据用户 ID 获取用户信息。
    """
    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            return user.name, user.platform_id, user.score, user.favorite_id
        else:
            logger.warning(f"[Database] User with ID {user_id} not found.")
            raise UserNotFoundError(f"User with ID {user_id} not found.")
    except Exception as e:
        logger.error(f"[Database] Error retrieving user with ID {user_id}: {e}")
        raise DatabaseOperationError(f"Error retrieving user with ID {user_id}: {e}")


def update_user_score(user_id: str, new_score: int) -> None:
    """
    更新用户的分数，并增加 score_update_count。
    """
    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            user.score = new_score
            user.score_update_count += 1
            session.commit()
            logger.info(
                f"[Database] User with ID {user_id} score updated to {new_score}, score_update_count incremented to {user.score_update_count}."
            )
        else:
            logger.warning(f"[Database] User with ID {user_id} not found.")
            raise UserNotFoundError(f"User with ID {user_id} not found.")
    except Exception as e:
        session.rollback()
        logger.error(f"[Database] Error updating score for user with ID {user_id}: {e}")
        raise DatabaseOperationError(
            f"Error updating score for user with ID {user_id}: {e}"
        )


def update_user_data(user_id: str, data: str) -> None:
    """
    更新用户的自定义数据。
    """
    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            user.data = data
            session.commit()
            logger.info(f"[Database] User with ID {user_id} data updated to {data}.")
        else:
            logger.warning(f"[Database] User with ID {user_id} not found.")
            raise UserNotFoundError(f"User with ID {user_id} not found.")
    except Exception as e:
        session.rollback()
        logger.error(f"[Database] Error updating data for user with ID {user_id}: {e}")
        raise DatabaseOperationError(
            f"Error updating data for user with ID {user_id}: {e}"
        )


def delete_user(user_id: str) -> None:
    """
    删除用户。
    """
    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            session.delete(user)
            session.commit()
            logger.info(f"[Database] User with ID {user_id} deleted.")
        else:
            logger.warning(f"[Database] User with ID {user_id} not found.")
            raise UserNotFoundError(f"User with ID {user_id} not found.")
    except Exception as e:
        session.rollback()
        logger.error(f"[Database] Error deleting user with ID {user_id}: {e}")
        raise DatabaseOperationError(f"Error deleting user with ID {user_id}: {e}")


def get_user_data(user_id: str) -> Optional[str]:
    """
    获取用户的自定义数据。
    """
    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            return user.data
        else:
            logger.warning(f"[Database] User with ID {user_id} not found.")
            return None
    except Exception as e:
        logger.error(
            f"[Database] Error retrieving data for user with ID {user_id}: {e}"
        )
        raise DatabaseOperationError(
            f"Error retrieving data for user with ID {user_id}: {e}"
        )


# Call this function when your application is shutting down
def shutdown_session():
    SessionLocal.remove()
