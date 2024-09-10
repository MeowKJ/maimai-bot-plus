from botpy.message import GroupMessage, Message
from botpy import logger

from src.libraries.common.message.message import MixMessage

from .handlers import search_by_args


async def get_song_by_alias(message: GroupMessage | Message):
    mix_message = MixMessage(message)
    args = mix_message.get_args("查歌")
    await search_by_args(args, mix_message)


async def get_song_score_by_alias(message: GroupMessage | Message):
    mix_message = MixMessage(message)
    args = mix_message.get_args("单曲成绩")
    await search_by_args(args, mix_message, is_score=True)


async def handle_what_song(message: GroupMessage | Message):
    mix_message = MixMessage(message)
    if "是什么歌" in message.content:
        args = mix_message.get_args("是什么歌", 0)
        if args:
            logger.info(f"[SONGINFO] {args} 是什么歌")
            await search_by_args(args, mix_message)

    if "的成绩" in message.content:
        args = mix_message.get_args("的成绩", 0)
        if args:
            logger.info(f"[SONGINFO] {args} 的成绩")
            await search_by_args(args, mix_message, is_score=True)
    return False


# 定义支持的指令及其处理函数（指令名应为小写）
COMMANDS = {
    "查歌": get_song_by_alias,
    "单曲成绩": get_song_by_alias,
}

DEFAULT_HANDLER = handle_what_song


# 默认大写的插件名
COMMAND_NAME = "SONG_INFO"

# 指令范围
COMMAND_SCOPE = "both"
