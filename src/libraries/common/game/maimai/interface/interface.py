from .types.types import *

from src.libraries.assets.get import assets


class Interface:

    def __init__(self, id: str, platform_id: str):
        self.id = id
        self.platform_id = platform_id

    async def fetch_user(self) -> None:
        pass

    async def fetch_single_song_socre(self, song_id: int) -> Song:
        pass

    async def fetch_b50_data(self) -> Dict[str, Song]:
        pass

    async def _get_total_song_data(self):
        BASE_API = ""
