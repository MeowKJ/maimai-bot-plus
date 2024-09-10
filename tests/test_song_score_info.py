import pytest
from PIL import Image
from src.libraries.common.game.maimai import Song, MaimaiUser

# test module
from src.plugins.song_info.draw import create_song_info_image


@pytest.mark.asyncio
async def test_create_song_info_image_show():
    # 创建 MaimaiUser 并获取一个 Song 对象
    user = MaimaiUser(0, 1)
    print(user)

    song = await user.fetch_single_song_score(11165)

    print(song)
    # 调用异步函数生成图片
    image = await create_song_info_image(song)

    # 显示生成的图片，让你肉眼检查
    image.show()

    # 直接通过测试，目的是肉眼检查图片是否正确
    assert True
