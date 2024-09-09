from typing import Any, Dict, List, Optional, Tuple, Union
from enum import Enum
from .interface.interface import Interface
from .interface.platform.fish import DivingFishInterface
from .interface.platform.lxns import LxnsInterface

# 枚举
from .interface.types.enums import *
from .interface.types.types import *

from config import LXNS_API_SECRET


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

    # 成绩接口
    interface: Interface | DivingFishInterface | LxnsInterface

    def __init__(self, id: str, user_platform: int) -> None:
        """初始化 MaimaiUser 类。

        Args:
            id (str): 用户ID。
            user_platform (int): 用户平台。

        """
        self.id = id
        self.user_platform = user_platform
        if user_platform == MaimaiUserPlatform.DIVING_FISH.value:
            self.interface = DivingFishInterface(id, user_platform)
        elif user_platform == MaimaiUserPlatform.LXNS.value:
            self.interface = LxnsInterface(id, user_platform, LXNS_API_SECRET)
        else:
            raise ValueError("Invalid user platform.")

    async def fetch_single_song_socre(self, song_id: int) -> Song:
        """获取单曲成绩。

        Args:
            song_id (int): 歌曲ID。

        """
        if not song_id:
            return None
        return await self.interface.fetch_single_song_socre(song_id)

    async def fetch(self, user_info: Dict[str, Any]) -> None:
        """获取用户信息。

        Args:
            user_info (Dict[str, Any]): 用户信息。

        """

    def __str__(self) -> str:
        """返回用户名称。

        Returns:
            str: 用户名称。

        """
        return self.username or self.id

    def __repr__(self) -> str:
        """返回用户名称。

        Returns:
            str: 用户名称。

        """
        return self.username or self.id

    def __eq__(self, other: Any) -> bool:
        """判断两个用户是否相等。

        Args:
            other (Any): 另一个用户。

        Returns:
            bool: 是否相等。

        """
        if not isinstance(other, MaimaiUser):
            return False
        return self.id == other.id and self.user_platform == other.user_platform

    def __hash__(self) -> int:
        """返回用户的哈希值。

        Returns:
            int: 用户的哈希值。

        """
        return hash((self.id, self.user_platform))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_platform": self.user_platform,
            "username": self.username,
            "avatar": self.avatar,
            "rating": self.rating,
            "course_rank": self.course_rank,
            "class_rank": self.class_rank,
            "trophy": self.trophy,
            "nameplate_id": self.nameplate_id,
            "frame_id": self.frame_id,
        }
