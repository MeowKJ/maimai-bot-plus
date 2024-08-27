from typing import List, Optional
import aiohttp


class FetchError(Exception):
    """Base class for all fetch-related exceptions."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(f"{status_code}: {message}" if status_code else message)


class DataNotFoundError(FetchError):
    """Exception raised when data is not found."""

    pass


class AuthorizationError(FetchError):
    """Exception raised for authorization issues."""

    pass


class ServiceUnavailableError(FetchError):
    """Exception raised when the service is unavailable."""

    pass


class SongData:
    def __init__(self, **kwargs):
        self.achievements = kwargs.get("achievements", 0)
        self.ds = kwargs.get("ds", 0)
        self.dx_score = kwargs.get("dx_score", 0)
        self.fc = kwargs.get("fc", "")
        self.fs = kwargs.get("fs", "")

        self.level = kwargs.get("level", "")
        self.level_index = kwargs.get("level_index", 0)
        self.rating = kwargs.get("rating", 0)
        self.rating_icon = kwargs.get("rating_icon", "")
        self.song_id = kwargs.get("song_id", 0)
        self.title = kwargs.get("title", "")
        self.type = kwargs.get("type", "")

        self.total_dxscore = 0

    @classmethod
    def from_data_luoxue(cls, data1):
        id_value = data1.get("id", 0)

        # 处理 id 大于 1000 的情况
        if id_value > 1000:
            id_value += 10000

        return cls(
            achievements=data1["achievements"],
            ds=data1.get("level", 0),
            dx_score=data1.get("dx_score", 0),
            fc=data1.get("fc", ""),
            fs=data1.get("fs", ""),
            level=data1.get("level", ""),
            level_index=data1.get("level_index", 0),
            rating=int(data1.get("dx_rating", 0)),
            rating_icon=data1.get("rate", ""),
            song_id=id_value,  # 更新 id 的值
            title=data1.get("song_name", ""),
            type="sd" if data1.get("type") == "standard" else "dx",
        )

    @classmethod
    def from_data_divingfish(cls, data2):
        return cls(
            achievements=data2["achievements"],
            ds=data2.get("ds", 0),
            dx_score=data2.get("dxScore", 0),
            fc=data2.get("fc", ""),
            fs=data2.get("fs", ""),
            level=data2.get("level", ""),
            level_index=data2.get("level_index", 0),
            rating=data2.get("ra", 0),
            rating_icon=data2.get("rate", ""),
            song_id=data2.get("song_id", 0),
            title=data2.get("title", ""),
            type=data2.get("type"),
        )


class Player:
    def __init__(
        self,
        username,
        guild_id,
        favorite_id=0,
        avatar_url="",
        api_secret="",
    ):
        self.username = username
        self.guild_id = guild_id

        self.avatar_url = avatar_url
        self.avatar_id = 0

        self.nickname = username
        self.rating = 0

        self.course_rank = None
        self.class_rank = None
        self.name_plate = None
        self.star = None

        self.song_data_b15: List[SongData] = []
        self.song_data_b35: List[SongData] = []

        self.song_data_b15_total = 0
        self.song_data_b35_total = 0
        self.api_secret = api_secret

        # 喜欢的音击小女孩 ID
        self.favorite_id = favorite_id

    async def fetch_songs_data(self, auth_headers):
        base_api = "https://maimai.lxns.net"
        async with aiohttp.request(
            "GET",
            f"{base_api}/api/v0/maimai/song/list?notes=true",
            headers=auth_headers,
        ) as resp:
            if resp.status != 200:
                raise ServiceUnavailableError("Unable to fetch song list.", resp.status)
            obj = await resp.json()
            return obj["songs"]

    def update_level_and_append(
        self, song_list, songs_data, target_list, from_what="lxns"
    ):
        for i in song_list:
            if from_what == "fish":
                matching_song = next(
                    (song for song in songs_data if song["id"] == i["song_id"] % 10000),
                    None,
                )
            else:
                matching_song = next(
                    (song for song in songs_data if song["id"] == i["id"]), None
                )
            if matching_song:
                song_type = "standard" if i["type"] == "SD" else i["type"].lower()
                if from_what != "fish":
                    i["level"] = (
                        f'{matching_song["difficulties"][song_type][i["level_index"]]["level_value"]:.1f}'
                    )
                if from_what == "fish":
                    song_data = SongData.from_data_divingfish(i)
                else:
                    song_data = SongData.from_data_luoxue(i)
                song_data.total_dxscore = (
                    matching_song["difficulties"][song_type][i["level_index"]]["notes"][
                        "total"
                    ]
                    * 3
                )
                target_list.append(song_data)

    async def fetch_divingfish(self):
        async with aiohttp.request(
            "POST",
            "https://www.diving-fish.com/api/maimaidxprober/query/player",
            json={"username": self.username, "b50": True},
        ) as resp:
            if resp.status == 200:
                obj = await resp.json()

                self.nickname = obj["nickname"]
                self.rating = obj["rating"]
                self.course_rank = obj["additional_rating"] + 1

                auth_headers = {}

                songs_data = await self.fetch_songs_data(auth_headers)

                self.update_level_and_append(
                    obj["charts"]["dx"], songs_data, self.song_data_b15, "fish"
                )
                self.update_level_and_append(
                    obj["charts"]["sd"], songs_data, self.song_data_b35, "fish"
                )

                self.song_data_b15_total = sum(
                    song.rating for song in self.song_data_b15
                )
                self.song_data_b35_total = sum(
                    song.rating for song in self.song_data_b35
                )

            elif resp.status == 404:
                raise DataNotFoundError("Data not found on Diving Fish.", resp.status)
            else:
                raise ServiceUnavailableError(
                    "Unable to fetch data from Diving Fish.", resp.status
                )

    async def fetch_luoxue(self):
        base_api = "https://maimai.lxns.net"
        auth_headers = {
            "Authorization": self.api_secret,
        }
        async with aiohttp.request(
            "GET",
            f"{base_api}/api/v0/maimai/player/qq/{self.username}",
            headers=auth_headers,
        ) as resp:
            if resp.status == 404:
                raise DataNotFoundError(
                    "Data not found on Luo Xue. Please check if the QQ number is consistent.",
                    resp.status,
                )
            elif resp.status != 200:
                raise ServiceUnavailableError(
                    "Unable to query your b50 at the moment.", resp.status
                )

            obj = await resp.json()
            if obj["code"] == 403:
                raise AuthorizationError(
                    "Option [Allow Reading Player Information] is not enabled.", 403
                )
            elif obj["code"] == 404:
                raise DataNotFoundError(
                    f"Data for [{self.username}] not found. Please check if the QQ number is consistent.",
                    404,
                )
            elif obj["code"] != 200:
                raise ServiceUnavailableError(
                    "Unable to query your b50 at the moment.", obj["code"]
                )

            self.nickname = obj["data"].get("name")
            self.rating = obj["data"].get("rating")
            self.class_rank = obj["data"].get("class_rank")
            self.course_rank = obj["data"].get("course_rank")
            self.star = obj["data"].get("star")
            self.avatar_id = obj["data"]["icon"].get("id")

            friend_code = obj["data"].get("friend_code")
            self.name_plate = obj["data"].get("name_plate", {}).get("id")

        songs_data = await self.fetch_songs_data(auth_headers)

        async with aiohttp.request(
            "GET",
            f"{base_api}/api/v0/maimai/player/{friend_code}/bests",
            headers=auth_headers,
        ) as resp:
            if resp.status == 404:
                raise DataNotFoundError(
                    "Data not found. Please check if the QQ number is consistent.",
                    resp.status,
                )
            elif resp.status != 200:
                raise ServiceUnavailableError(
                    "Unable to query your b50 at the moment.", resp.status
                )

            obj = await resp.json()
            if obj["code"] == 403:
                raise AuthorizationError(
                    "Option [Allow Reading Chart Scores] is not enabled.", 403
                )
            elif obj["code"] != 200:
                raise ServiceUnavailableError(
                    "Unable to query your b50 at the moment.", obj["code"]
                )

            self.update_level_and_append(
                obj["data"]["standard"], songs_data, self.song_data_b35
            )
            self.update_level_and_append(
                obj["data"]["dx"], songs_data, self.song_data_b15
            )

            self.song_data_b15_total = obj["data"]["dx_total"]
            self.song_data_b35_total = obj["data"]["standard_total"]
