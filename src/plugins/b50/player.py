from typing import List
from src.libraries.common.game.maimai import MaimaiUser, SongDifficulty, UserInfo


class B50Player:
    def __init__(
        self,
        username,
        guild_id,
        favorite_id=0,
        avatar_url="",
    ):
        self.username = username
        self.guild_id = guild_id
        self.avatar_url = avatar_url

        self.song_data_b15: List[SongDifficulty] = []
        self.song_data_b35: List[SongDifficulty] = []
        self.user_info: UserInfo = None
        # 喜欢的音击小女孩 ID
        self.favorite_id = favorite_id

    async def enrich(self, user: MaimaiUser):
        data = await user.fetch_best50_song_score()
        self.song_data_b15 = data["b15"]
        self.song_data_b35 = data["b35"]
        self.user_info: UserInfo = data["user_info"]
        if not self.user_info.avatar:
            self.user_info.avatar = self.avatar_url
