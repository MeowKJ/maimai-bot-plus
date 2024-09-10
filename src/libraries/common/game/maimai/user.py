from typing import Any, Dict, List, Union

from .interface.platform.fish import DivingFishInterface
from .interface.platform.lxns import LxnsInterface

# 枚举
from .interface.types.enums import MaimaiUserPlatform
from .interface.types.types import Song, UserInfo

from config import LXNS_API_SECRET


class MaimaiUser:
    """代表一个 Maimai 用户的类"""

    # 用户属性定义
    user_platform: int
    id: str

    # 成绩接口
    interface: Union[DivingFishInterface, LxnsInterface]

    def __init__(self, id: str, user_platform: int) -> None:
        """初始化 MaimaiUser 类。

        Args:
            id (str): 用户ID。
            user_platform (int): 用户平台。
        """
        self.id = id
        self.user_platform = user_platform
        self.interface = self._initialize_interface(user_platform)

    def _initialize_interface(
        self, user_platform: int
    ) -> Union[DivingFishInterface, LxnsInterface]:
        """初始化对应的接口。

        Args:
            user_platform (int): 用户平台。

        Returns:
            Union[DivingFishInterface, LxnsInterface]: 对应的接口实例。
        """
        if user_platform == MaimaiUserPlatform.DIVING_FISH.value:
            return DivingFishInterface(self.id, user_platform)
        elif user_platform == MaimaiUserPlatform.LXNS.value:
            return LxnsInterface(self.id, user_platform, LXNS_API_SECRET)
        else:
            raise ValueError("Invalid user platform.")

    async def fetch_single_song_score(self, song_id: int) -> Union[Song, None]:
        """获取单曲成绩。

        Args:
            song_id (int): 歌曲ID。

        Returns:
            Union[Song, None]: 单曲成绩对象或 None。
        """
        if not song_id:
            return None
        return await self.interface.fetch_single_song_score(song_id)

    async def fetch_best50_song_score(self) -> Dict[str, Union[UserInfo, List[Song]]]:
        """获取B50成绩。

        Returns:
            tuple[List[Song], List[Song]]: B50成绩列表。
        """
        return await self.interface.fetch_best50_song_score()

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
        """将用户对象转换为字典。

        Returns:
            Dict[str, Any]: 包含用户属性的字典。
        """
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
