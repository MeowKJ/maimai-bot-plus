from typing import List
from src.libraries.common.game.maimai import MaimaiUser, SongDifficulty, UserInfo


class Player:
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
        self.avatar_id = 0

        self.nickname = username
        self.rating = 0

        self.course_rank = None
        self.class_rank = None
        self.name_plate = None
        self.star = None

        self.song_data_b15: List[SongDifficulty] = []
        self.song_data_b35: List[SongDifficulty] = []

        # 喜欢的音击小女孩 ID
        self.favorite_id = favorite_id

    async def enrich(self, user: MaimaiUser):
        data = await user.fetch_best50_song_score()
        self.song_data_b15 = data["b15"]
        self.song_data_b35 = data["b35"]
        user_info: UserInfo = data["user_info"]

        self.nickname = user_info.username
        self.rating = user_info.rating
        self.course_rank = user_info.course_rank
        self.class_rank = user_info.class_rank
        self.trophy = user_info.trophy
        self.name_plate = user_info.nameplate_id
        self.frame = user_info.frame_id

        if user_info.avatar.isdigit():
            self.avatar_id = user_info.avatar
