from typing import List
from pathlib import Path

from botpy.message import GroupMessage, Message
from botpy import logger

from src.libraries.common.message.message import MixMessage
from src.libraries.assets import assets, JSONType

from src.libraries.common.file.temp import TempFileManager

from src.libraries.common.game.maimai import Song

from .draw import create_selected_song_image, create_song_info_image


async def get_song_info_id_list_from_alias(alias: str) -> List[int]:
    alias = alias.lower().replace(" ", "")
    alias_data = await assets.get_json(JSONType.ALIAS)
    return [
        int(song_id)
        for song_id, aliases in alias_data.items()
        if alias in [a.lower().replace(" ", "") for a in aliases]
    ]


async def get_song_info(alias="", songid=0, debug=False):

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

    info_image = await create_song_info_image(song_info)

    return True, info_image


async def search_by_args(args: str, mix_message: MixMessage):
    if not args:
        await mix_message.reply(
            content=(
                "请输入歌曲别名或ID\n" "例如：/查歌 xxx\n" "你也可以直接问xxx是什么歌\n"
            )
        )
    # try:
    if args.isdigit():
        song_id = int(args)
        image_url_list = await get_song_info(songid=song_id)
        if image_url_list and len(image_url_list) > 0:
            await mix_message.reply(file_image=image_url_list[0])
        else:
            await mix_message.reply(content=f"😢没有找到ID=[{song_id}]的乐曲")

    else:
        alias = args
        flag, image = await get_song_info(alias=alias)
        temp_file_manager = TempFileManager()
        if flag:
            path, name = temp_file_manager.create_temp_image_file(
                image=image, suffix=".jpg", quality=60
            )
            await mix_message.reply(file_image=Path(path))
        else:
            if image:
                path, name = temp_file_manager.create_temp_image_file(
                    image=image, suffix=".jpg"
                )
                await mix_message.reply(
                    content=f"找到了多个被称为[{alias}]的乐曲, 使用ID查看详细信息",
                    file_image=Path(path),
                )
            else:
                await mix_message.reply(content=f"😢没有找到被称作为[{alias}]的乐曲")

    # except Exception as e:
    #     logger.error(f"[SONGINFO] Get Error {e}")
    #     await mix_message.reply(content="获取歌曲数据出错啦")


async def get_song_by_alias(message: GroupMessage | Message):
    mix_message = MixMessage(message)
    args = mix_message.get_args("查歌")
    await search_by_args(args, mix_message)


async def handle_what_song(message: GroupMessage | Message):
    mix_message = MixMessage(message)
    if "是什么歌" in message.content:
        args = mix_message.get_args("是什么歌", 0)
        if args:
            logger.info(f"[SONGINFO] {args} 是什么歌")
            await search_by_args(args, mix_message)
    return False


# 定义支持的指令及其处理函数（指令名应为小写）
COMMANDS = {
    "查歌": get_song_by_alias,
}

DEFAULT_HANDLER = handle_what_song


# 默认大写的插件名
COMMAND_NAME = "SONG_INFO"

# 指令范围
COMMAND_SCOPE = "both"
