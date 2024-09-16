import pytest
import sys

print(sys.path)

# test module
from src.plugins.b50.command import *


@pytest.mark.asyncio
async def test_create_song_info_image_show():
    username = "komooooo"
    platform_id = 0
    user_id = 1
    player = B50Player(
        username,
        user_id,
        favorite_id=0,
        avatar_url="https://avatars.githubusercontent.com/u/65823167?v=4",
    )
    maimai_player = MaimaiUser(id=username, user_platform=platform_id)
    await player.enrich(maimai_player)

    drawBest = DrawBest(player)
    draw = await drawBest.draw()
    draw.show()
    assert True
