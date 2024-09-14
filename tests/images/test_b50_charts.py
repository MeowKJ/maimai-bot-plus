import pytest
from PIL import Image
from src.libraries.common.game.maimai import Song, MaimaiUser

# test module
from src.plugins.b50.charts import generate_pie_chart


@pytest.mark.asyncio
async def test_create_song_info_image_show():
    # 创建 MaimaiUser 并获取一个 Song 对象

    generate_pie_chart()
    assert True
