from __future__ import annotations

from typing import Dict, List, Union, TYPE_CHECKING

import aiohttp
from botpy import logger
from src.libraries.assets import assets, JSONType

from .interface import Interface

from ..enums import *
from .._types import UserInfo, SongDifficulty, UserDifficultyScore

if TYPE_CHECKING:
    from ..song import Song


from ..maimai import MaimaiHelper


BASE_API = "https://www.diving-fish.com/api/maimaidxprober/query"


class DivingFishInterface(Interface):
    nickname: str

    def __init__(self, id: str, platform_id: str):
        super().__init__(id, platform_id)

    async def fetch_single_song_score(self, id: int) -> Song:
        pass

    async def fetch_best50_song_score(self) -> Dict[str, Union[UserInfo, List[Song]]]:
        # 第一步 获取用户信息
        async with aiohttp.ClientSession() as session:
            async with session.post(
                BASE_API + "/player",
                json={"username": self.id, "b50": True},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"[Fish] 用户信息获取成功: {self.id}")
                else:
                    logger.error(
                        f"[Fish] 用户信息获取失败: {self.id} {response.status}"
                    )
                    return None

        user_info = UserInfo(
            username=data["nickname"],
            avatar="",
            rating=data["rating"],
            course_rank=data["additional_rating"] + 1,
            class_rank=0,
            trophy="",
            nameplate_id=0,
            frame_id=0,
        )
        b15 = []
        b35 = []
        # 第二步 获取B50成绩
        charts = data["charts"]["dx"]

        for song_data in charts:
            id = MaimaiHelper.common_to_lxns_songid(song_data["song_id"])
            song_difficulty = SongDifficulty(
                id=id,
                level=song_data["ds"],
                level_label=song_data["level"],
                level_index=song_data["level_index"],
                title=song_data["title"],
                song_type=SongType.get_type_by_name(song_data["type"]),
            )

            user_score = UserDifficultyScore(
                level_index=song_data["level_index"],
                achievements=song_data["achievements"],
                rate=SongRateType.get_type_by_name(song_data["rate"]),
                rating=int(song_data["ra"]),
                fc=FCType.get_type_by_name(song_data["fc"]),
                fs=FSType.get_type_by_name(song_data["fs"]),
                dx_score=song_data["dxScore"],
            )
            song_difficulty.user_score = user_score
            b15.append(song_difficulty)

        charts = data["charts"]["sd"]
        for song_data in charts:
            id = MaimaiHelper.common_to_lxns_songid(song_data["song_id"])
            song_difficulty = SongDifficulty(
                id=id,
                level=song_data["ds"],
                level_label=song_data["level"],
                level_index=song_data["level_index"],
                title=song_data["title"],
                song_type=SongType.get_type_by_name(song_data["type"]),
            )

            user_score = UserDifficultyScore(
                level_index=song_data["level_index"],
                achievements=song_data["achievements"],
                rate=SongRateType.get_type_by_name(song_data["rate"]),
                rating=int(song_data["ra"]),
                fc=FCType.get_type_by_name(song_data["fc"]),
                fs=FSType.get_type_by_name(song_data["fs"]),
                dx_score=song_data["dxScore"],
            )
            song_difficulty.user_score = user_score
            b35.append(song_difficulty)

        total_songs_data_raw = await assets.get_json(JSONType.LXNS_SONGS_INFO)
        total_songs_data = total_songs_data_raw["songs"]

        def enrich_difficulty_score(
            songs: List[SongDifficulty],
        ) -> List[SongDifficulty]:
            for song_data in total_songs_data:
                for song in songs:
                    if song.id == song_data["id"]:
                        song.dx_rating_max = (
                            song_data["difficulties"][song.song_type.value][
                                song.level_index
                            ]["notes"]["total"]
                            * 3
                        )
                        # 乐曲id变更
                        song.id = MaimaiHelper.lxns_to_common_songid(song.id)
            return songs

        b15 = enrich_difficulty_score(b15)
        b35 = enrich_difficulty_score(b35)

        return {
            "user_info": user_info,
            "b15": b15,
            "b35": b35,
        }
