import pytest
import sys
print(sys.path)

# test module
from src.plugins.song_info.draw import create_song_info_image, create_song_score_image

from src.libraries.common.game.maimai import MaimaiUser, Song


@pytest.mark.asyncio
async def test_create_song_info_image_show():
    # 创建 MaimaiUser 并获取一个 Song 对象
    user = MaimaiUser(1379724301, 1)
    print(user)
    song = Song(11165)
    if not await song.enrich_all(user):
        assert False

    print(song)
    # 调用异步函数生成图片
    image2 = await create_song_score_image(song)
    image = await create_song_info_image(song)

    # 显示生成的图片，让你肉眼检查
    image.show()
    image2.show()

    # 直接通过测试，目的是肉眼检查图片是否正确
    assert True
