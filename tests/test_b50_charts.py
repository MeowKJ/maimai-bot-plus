import pytest
import sys

print(sys.path)


# test module
from src.plugins.b50.charts import generate_pie_chart

from src.libraries.common.game.maimai import Song, MaimaiUser


@pytest.mark.asyncio
async def test_create_song_info_image_show():
    generate_pie_chart()
    assert True
