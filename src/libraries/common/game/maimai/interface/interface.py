from typing import Dict

from .types.types import *


class Interface:

    def __init__(self, id: str, platform_id: str):
        self.id = id
        self.platform_id = platform_id

    async def fetch_user(self) -> None:
        pass

    async def fetch_single_song_score(self, song_id: int) -> Song:
        pass

    async def append_user_score(self, song: Song) -> Song:
        pass

    async def fetch_b50_data(self) -> Dict[str, Song]:
        pass

    async def _get_total_song_data(self):
        BASE_API = ""
