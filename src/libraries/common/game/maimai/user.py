from typing import Any, Dict, List, Optional, Tuple, Union
from enum import Enum

# 枚举
from .enums import UserPlatform


class MaimaiUser:

    # 用户平台
    user_platform: int

    # 用户ID
    id: str

    # 用户名称
    username: str

    # 用户头像(图片地址)
    avatar: str

    # 用户Rating
    rating: int

    # 用户course_rank(段位, 初学者0, 初段-十段1-10, 真初段-真十段12-21)
    course_rank: int

    # 用户友人对战等级(1-B4)
    class_rank: int

    # 用户称号
    trophy: str

    # 用户姓名框ID
    nameplate_id: int

    # 用户背景版ID
    frame_id: int

    def get(self, user_id: int) -> Dict[str, Any]:
        user = self._get_user(user_id)
        return {
            "user_id": user.id,
            "name": user.name,
            "level": user.level,
            "exp": user.exp,
            "play_count": user.play_count,
            "win_count": user.win_count,
            "lose_count": user.lose_count,
            "draw_count": user.draw_count,
            "win_rate": user.win_rate,
            "rating": user.rating,
            "rating_deviation": user.rating_deviation,
            "rating_volatility": user.rating_volatility,
            "rating_history": user.rating_history,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

    def _get_user(self, user_id: int) -> User:
        user = self.session.query(User).get(user_id)
        if user is None:
            raise UserNotFoundError()
        return user