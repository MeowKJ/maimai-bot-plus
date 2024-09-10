from typing import Dict, List, Union

import aiohttp
from botpy import logger
from ..interface import Interface
from ..types.types import (
    Song,
    SongType,
    UserInfo,
    SongDifficulty,
    UserDifficultyScore,
    FSType,
    FCType,
    SongRateType,
)
from ...maimai import MaimaiHelper
from src.libraries.assets import assets, JSONType, AssetType

BASE_API = "https://maimai.lxns.net/api/v0/maimai"


class LxnsInterface(Interface):
    friend_code: str = None
    lxns_api: str

    def __init__(self, id: str, platform_id: str, lxns_api: str):
        super().__init__(id, platform_id)
        self.lxns_api = lxns_api

    async def _get_friend_code(self):
        async with aiohttp.ClientSession() as session:
            url = f"{BASE_API}/player/qq/{self.id}"
            async with session.get(
                url=url,
                headers={"Authorization": self.lxns_api},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.friend_code = str(data["data"]["friend_code"])
                else:
                    self.friend_code = None

    async def fetch_user_info(self) -> UserInfo:
        """获取用户信息。

        Returns:
            UserInfo: 用户信息。
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                BASE_API + f"/player/qq/{self.id}",
                headers={"Authorization": self.lxns_api},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    data = data["data"]
                    logger.info(f"[LXNS] 用户信息获取成功: {self.id}")
                else:
                    logger.error(
                        f"[LXNS] 用户信息获取失败: {self.id} {response.status}"
                    )
                    return None
        return UserInfo(
            username=data.get("name", "未知"),
            avatar=str(data.get("icon", {}).get("id", "")),
            rating=data.get("rating", 0),
            course_rank=data.get("course_rank", 0),
            class_rank=data.get("class_rank", 0),
            trophy=data.get("trophy", {}).get("name", ""),
            nameplate_id=data.get("name_plate", {}).get("id"),
            frame_id=data.get("frame", {}).get("id"),
        )

    # async def fetch_single_song_score(self, id: int, **kwargs) -> Song:

    #     if not self.friend_code:
    #         await self._get_friend_code()
    #     if id < 10000:
    #         song_id = id
    #         song_type = SongType.STANDARD.value
    #     elif id < 100000:
    #         song_id = id % 10000
    #         song_type = SongType.DX.value
    #     else:
    #         song_id = id
    #         song_type = SongType.UTAGE.value

    #     async with aiohttp.ClientSession() as session:
    #         async with session.get(
    #             BASE_API + f"/player/{self.friend_code}/bests/",
    #             headers={"Authorization": self.lxns_api},
    #             params={"song_id": song_id, "song_type": song_type},
    #         ) as response:
    #             if response.status == 200:
    #                 data = await response.json()
    #                 data = data["data"]
    #             else:
    #                 return None
    #     song = Song(id)

    #     if kwargs.get("enrich", True):
    #         await song.enrich()

    #     for score in data:
    #         user_difficulty_score = UserDifficultyScore(
    #             level_index=score["level_index"],
    #             achievements=score["achievements"],
    #             dx_score=score["dx_score"],
    #             rating=int(score["dx_rating"]),
    #             rate=SongRateType.get_type_by_name(score["rate"]),
    #             fc=FCType.get_type_by_name(score["fc"]),
    #             fs=FSType.get_type_by_name(score["fs"]),
    #         )
    #         song.add_user_score(user_difficulty_score)

    #     return song

    async def append_user_score(self, song: Song) -> Song:

        if not self.friend_code:
            await self._get_friend_code()
        if song.id < 10000:
            song_id = song.id
            song_type = SongType.STANDARD.value
        elif song.id < 100000:
            song_id = song.id % 10000
            song_type = SongType.DX.value
        else:
            song_id = song.id
            song_type = SongType.UTAGE.value

        async with aiohttp.ClientSession() as session:
            async with session.get(
                BASE_API + f"/player/{self.friend_code}/bests/",
                headers={"Authorization": self.lxns_api},
                params={"song_id": song_id, "song_type": song_type},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    data = data["data"]
                else:
                    return None

        for score in data:
            user_difficulty_score = UserDifficultyScore(
                level_index=score["level_index"],
                achievements=score["achievements"],
                dx_score=score["dx_score"],
                rating=int(score["dx_rating"]),
                rate=SongRateType.get_type_by_name(score["rate"]),
                fc=FCType.get_type_by_name(score["fc"]),
                fs=FSType.get_type_by_name(score["fs"]),
            )
            song.add_user_score(user_difficulty_score)

        return song

    async def fetch_best50_song_score(self) -> Dict[str, Union[UserInfo, List[Song]]]:
        # if not self.friend_code:
        #     await self._get_friend_code()
        # 第一步 获取用户信息h

        async with aiohttp.ClientSession() as session:
            async with session.get(
                BASE_API + f"/player/qq/{self.id}",
                headers={"Authorization": self.lxns_api},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    data = data["data"]
                    logger.info(f"[LXNS] 用户信息获取成功: {self.id}")
                else:
                    logger.error(
                        f"[LXNS] 用户信息获取失败: {self.id} {response.status}"
                    )
                    return None
        # 结构体
        # Player
        # 玩家

        # 字段名	类型	说明
        # name	string	游戏内名称
        # rating	int	玩家 DX Rating
        # friend_code	int	好友码
        # trophy	Trophy	仅获取玩家信息返回，称号
        # trophy_name	string	仅创建玩家信息必选，称号
        # course_rank	int	段位 ID
        # class_rank	int	阶级 ID
        # star	int	搭档觉醒数
        # icon	Icon	值可空，头像
        # name_plate	NamePlate	值可空，姓名框
        # frame	Frame	值可空，背景
        # upload_time	string	仅获取玩家信息返回，玩家被同步时的 UTC 时间

        self.friend_code = str(data["friend_code"])
        user_info = UserInfo(
            username=data.get("name", "未知"),
            avatar=str(data.get("icon", {}).get("id", "")),
            rating=data.get("rating", 0),
            course_rank=data.get("course_rank", 0),
            class_rank=data.get("class_rank", 0),
            trophy=data.get("trophy", {}).get("name", ""),
            nameplate_id=data.get("name_plate", {}).get("id"),
            frame_id=data.get("frame", {}).get("id"),
        )

        # 第二步 获取B50成绩
        async with aiohttp.ClientSession() as session:
            async with session.get(
                BASE_API + f"/player/{self.friend_code}/bests",
                headers={"Authorization": self.lxns_api},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    data = data["data"]
                    logger.info(f"[LXNS] B50 成绩获取成功: {self.id}")

                else:
                    return None

        b15 = []
        b35 = []

        # 字段名	类型	说明
        # id	int	曲目 ID
        # song_name	string	仅获取 Score 时返回，曲名
        # level	string	仅获取 Score 时返回，难度标级，如 14+
        # level_index	LevelIndex	难度
        # achievements	float	达成率
        # fc	FCType	值可空，FULL COMBO 类型
        # fs	FSType	值可空，FULL SYNC 类型
        # dx_score	int	DX 分数
        # dx_rating	float	仅获取 Score 时返回，DX Rating，计算时需要向下取整
        # rate	RateType	仅获取 Score 时返回，评级类型
        # type	SongType	谱面类型
        # play_time	string	值可空，游玩的 UTC 时间，精确到分钟
        # upload_time	string	仅获取 Score 时返回，成绩被同步时的 UTC 时间
        total_songs_data_raw = await assets.get_json(JSONType.LXNS_SONGS_INFO)
        total_songs_data = total_songs_data_raw["songs"]

        def enrich_difficulty_score(
            songs: List[SongDifficulty],
        ) -> List[SongDifficulty]:
            for song_data in total_songs_data:
                for song in songs:
                    if song.id == song_data["id"]:
                        # 乐曲的定数补充
                        song.level = song_data["difficulties"][song.song_type.value][
                            song.level_index
                        ]["level_value"]
                        # 乐曲dx分补充
                        song.dx_rating_max = (
                            song_data["difficulties"][song.song_type.value][
                                song.level_index
                            ]["notes"]["total"]
                            * 3
                        )
                        # 乐曲id变更
                        song.id = MaimaiHelper.lxns_to_common_songid(song.id)
            return songs

        for lx_song in data["standard"]:
            # id = MaimaiHelper.lxns_to_common_songid(lx_song["id"])

            # 乐曲的基本信息
            song = SongDifficulty(
                id=lx_song["id"],
                level_label=lx_song["level"],
                level_index=lx_song["level_index"],
                song_type=SongType.get_type_by_name(lx_song["type"]),
                title=lx_song["song_name"],
            )

            user_difficulty_score = UserDifficultyScore(
                level_index=song.level_index,
                achievements=lx_song["achievements"],
                dx_score=lx_song["dx_score"],
                rating=int(lx_song["dx_rating"]),
                rate=SongRateType.get_type_by_name(lx_song["rate"]),
                fc=FCType.get_type_by_name(lx_song["fc"]),
                fs=FSType.get_type_by_name(lx_song["fs"]),
            )

            song.user_score = user_difficulty_score
            b35.append(song)

        for lx_song in data["dx"]:
            # id = MaimaiHelper.lxns_to_common_songid(lx_song["id"])

            # 乐曲的基本信息
            song = SongDifficulty(
                id=lx_song["id"],
                level_label=lx_song["level"],
                level_index=lx_song["level_index"],
                song_type=SongType.get_type_by_name(lx_song["type"]),
                title=lx_song["song_name"],
            )

            user_difficulty_score = UserDifficultyScore(
                level_index=song.level_index,
                achievements=lx_song["achievements"],
                dx_score=lx_song["dx_score"],
                rating=int(lx_song["dx_rating"]),
                rate=SongRateType.get_type_by_name(lx_song["rate"]),
                fc=FCType.get_type_by_name(lx_song["fc"]),
                fs=FSType.get_type_by_name(lx_song["fs"]),
            )

            song.user_score = user_difficulty_score
            b15.append(song)

        # 补充乐曲的定数和dx分
        b15 = enrich_difficulty_score(b15)
        b35 = enrich_difficulty_score(b35)
        return {
            "user_info": user_info,
            "b15": b15,
            "b35": b35,
            "b15_total": data["dx_total"],
            "b35_total": data["standard_total"],
        }
