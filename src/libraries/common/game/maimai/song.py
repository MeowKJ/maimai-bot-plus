from __future__ import annotations

from typing import List, TYPE_CHECKING
import aiohttp
from botpy import logger

from .maimai import MaimaiHelper
from .enums import *
from ._types import *

if TYPE_CHECKING:
    from .user import MaimaiUser


class Song:
    # 歌曲ID
    id: int

    # 歌曲名
    title: str

    # 歌手名
    artist: str

    # BPM
    bpm: int

    # 曲目分类
    genre: str

    # 曲目版本
    version: str

    # 是否被禁用
    disabled: bool

    # 是否为新曲目
    isnew: bool

    # 是否含有Re:MASTER铺面
    has_re_master: bool

    # 歌曲类型
    song_type: SongType

    # 获取地图
    _map: str = ""

    # 铺面列表
    difficulties: List[SongDifficulty]

    # UTAGE铺面
    difficulties_utage: SongDifficultyUtage

    def __init__(self, id):
        self.id = id
        if self.id < 10000:
            self.song_type = SongType.STANDARD
        elif self.id < 100000:
            self.song_type = SongType.DX
        else:
            self.song_type = SongType.UTAGE
        self.difficulties = []
        self.difficulties_utage = None

    async def enrich(self):
        """
        丰富歌曲信息
        """
        lxns_id = MaimaiHelper.common_to_lxns_songid(self.id)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://maimai.lxns.net/api/v0/maimai/song/{lxns_id}"
            ) as response:
                if response.status == 200:
                    song = await response.json()
                else:
                    return False
        self.title = song["title"]
        self.artist = song["artist"]
        self.bpm = song["bpm"]
        self.genre = song["genre"]
        self.version = song["version"]
        logger.info(f"[LMAIMAI] 歌曲信息: {self.title} - {self.genre}")
        if "map" in song and self.song_type == SongType.DX:
            self._map = song["map"]

        # TODO: UTAGE铺面
        for i, song_info in enumerate(song["difficulties"][self.song_type.value]):

            notes = Notes(
                total=song_info["notes"]["total"],
                tap=song_info["notes"]["tap"],
                hold=song_info["notes"]["hold"],
                slide=song_info["notes"]["slide"],
                touch=song_info["notes"]["touch"],
                break_=song_info["notes"]["break"],
            )

            difficulty = SongDifficulty(
                # 定数
                level=song_info["level_value"],
                # 难度标签
                level_lable=song_info["level"],
                # 难度索引
                level_index=song_info["difficulty"],
                # 铺面作者
                note_designer=song_info["note_designer"],
                # 版本
                version=song_info["version"],
                # 音符
                notes=notes,
            )

            self._append_difficulty(difficulty)
        return True

    def add_user_score(self, user_score: UserDifficultyScore):
        """
        添加玩家成绩

        Args:
            user_score (UserDifficultyScore): 玩家成绩
        """
        for difficulty in self.difficulties:
            if difficulty.level_index == user_score.level_index:
                difficulty.user_score = user_score
                break

    async def enrich_all(self, user: MaimaiUser) -> bool:
        """
        丰富歌曲信息

        Args:
            user (MaimaiUser): 用户

        """
        if not await self.enrich():
            return False
        self = await user.append_user_score(self)
        return True

    def _append_difficulty(self, difficulty: SongDifficulty):
        """
        添加铺面

        Args:
            difficulty (SongDifficulty): 铺面
        """
        self.difficulties.append(difficulty)

    def __str__(self):
        return f"{self.id} - {self.title} - {self.genre}"
