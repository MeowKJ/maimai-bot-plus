from typing import List
from pathlib import Path


from src.libraries.common.message.message import MixMessage
from src.libraries.assets import assets, JSONType

from src.libraries.common.file.temp import TempFileManager

from src.libraries.common.game.maimai import Song, MaimaiUser

from src.libraries.database.crud import get_user_by_id
from .draw import (
    create_selected_song_image,
    create_song_info_image,
    create_song_score_image,
)


async def get_song_info_id_list_from_alias(alias: str) -> List[int]:
    alias = alias.lower().replace(" ", "")
    alias_data = await assets.get_json(JSONType.ALIAS)
    return [
        int(song_id)
        for song_id, aliases in alias_data.items()
        if alias in [a.lower().replace(" ", "") for a in aliases]
    ]


async def get_song_info_images(
    alias="", songid=0, debug=False, is_score=False, user_id=""
):

    if alias:
        matching_songs_id_list = await get_song_info_id_list_from_alias(alias)
    elif songid:
        matching_songs_id_list = [songid]
    else:
        return False, None

    # 保存匹配的曲目信息并分裂曲目
    song_data_list: List[Song] = []
    for song_id in matching_songs_id_list:
        song_data = Song(song_id)
        if not await song_data.enrich():
            continue
        song_data_list.append(song_data)

    # 没有找到匹配的曲目
    if len(song_data_list) == 0:
        return False, None

    # 存在多首匹配的曲目
    if len(song_data_list) > 1:
        selected_image = await create_selected_song_image(song_data_list)
        return False, selected_image

    # 开始绘图
    song_info = song_data_list[0]
    if is_score:
        name, platform_id, score, _ = get_user_by_id(user_id)
        user = MaimaiUser(name, platform_id)
        song_score_info = await user.append_user_score(song_info)
        info_image = await create_song_score_image(song_score_info)
    else:

        info_image = await create_song_info_image(song_info)

    return True, info_image


async def search_by_args(args: str, mix_message: MixMessage, is_score=False):
    """
    根据参数搜索歌曲信息

    Args:
        args (str): 参数
        mix_message (MixMessage): 消息对象

    Returns:
        None

    """
    if not args:
        await mix_message.reply(
            content=(
                "请输入歌曲别名或ID\n" "例如：/查歌 xxx\n" "你也可以直接问xxx是什么歌\n"
            )
        )
    # try:
    if args.isdigit():
        song_id = int(args)
        flag, image = await get_song_info_images(
            songid=song_id, is_score=is_score, user_id=mix_message.user_id
        )
        temp_file_manager = TempFileManager()
        if flag:
            path, name = temp_file_manager.create_temp_image_file(
                image=image, suffix=".jpg", quality=60
            )
            await mix_message.reply(file_image=path)
        else:
            await mix_message.reply(content=f"😢没有找到ID=[{song_id}]的乐曲")

    else:
        alias = args
        flag, image = await get_song_info_images(
            alias=alias, is_score=is_score, user_id=mix_message.user_id
        )
        temp_file_manager = TempFileManager()
        if flag:
            path, name = temp_file_manager.create_temp_image_file(
                image=image, suffix=".jpg", quality=60
            )
            await mix_message.reply(file_image=path)
        else:
            if image:
                path, name = temp_file_manager.create_temp_image_file(
                    image=image, suffix=".jpg"
                )
                await mix_message.reply(
                    content=f"找到了多个被称为[{alias}]的乐曲, 使用ID查看详细信息",
                    file_image=path,
                )
            else:
                await mix_message.reply(content=f"😢没有找到被称作为[{alias}]的乐曲")
