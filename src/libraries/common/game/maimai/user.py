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

    # async def fetch_single_song_score(
    #     self, song_id: int, **kwargs
    # ) -> Union[Song, None]:
    #     """获取单曲成绩。

    #     Args:
    #         song_id (int): 歌曲ID。
    #         **kwargs: 传递给下一个函数的其他参数。

    #     Returns:
    #         Union[Song, None]: 单曲成绩对象或 None。
    #     """
    #     if not song_id:
    #         return None
    #     # 将 song_id 传入，并把 kwargs 传递给下一个函数
    #     return await self.interface.fetch_single_song_score(song_id, **kwargs)

    async def append_user_score(self, song: Song) -> Song:
        """追加用户成绩。

        Args:
            song (Song): 歌曲对象。

        Returns:
            Song: 歌曲对象。
        """
        return await self.interface.append_user_score(song)

    async def fetch_best50_song_score(self) -> Dict[str, Union[UserInfo, List[Song]]]:
        """获取B50成绩。

        Returns:
            tuple[List[Song], List[Song]]: B50成绩列表。
        """
        return await self.interface.fetch_best50_song_score()

    async def fetch_user_info(self) -> UserInfo:
        """获取用户信息。

        Returns:
            UserInfo: 用户信息。
        """
        return await self.interface.fetch_user_info()

    def __str__(self) -> str:
        """返回用户名称。

        Returns:
            str: 用户名称。
        """
        return str(self.id)
