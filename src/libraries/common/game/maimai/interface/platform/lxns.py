from typing import Dict
from ..interface import Interface
from ..types.types import Song, SongType

import aiohttp


BASE_API = "https://maimai.lxns.net/api/v0/maimai"

USERDATA_QQ_API = f"{BASE_API}/player/qq/"


class LxnsInterface(Interface):
    friend_code: str
    lxns_api: str

    def __init__(self, id: str, platform_id: str, lxns_api: str):
        super().__init__(id, platform_id)
        self._get_friend_code()

    async def _get_friend_code(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                USERDATA_QQ_API + f"/{id}", headers={"Authorization": self.lxns_api}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.friend_code = str(data["data"]["friend_code"])
                else:
                    self.friend_code = None

    async def fetch_user(self) -> None:
        pass

    async def fetch_single_song_socre(self, id: int) -> Song:
        if id < 10000:
            song_id = id
            song_type = SongType.STANDARD.value
        elif id < 100000:
            song_id = id % 10000
            song_type = SongType.DX.value
        else:
            song_id = id
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

        song = Song(id)
        await song.enrich()
        return song

    async def fetch_b50_data(self) -> Dict[str, Song]:
        pass
