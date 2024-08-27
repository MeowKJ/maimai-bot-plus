import os
import time
import asyncio
import subprocess
from botpy.message import Message
from botpy import logger

from config import LXNS_API_SECRET
from src.libraries.database import add_or_update_user, get_user_by_id, update_user_score
from src.libraries.database.exceptions import DatabaseOperationError, UserNotFoundError

from .tools import is_fish_else_lxns
from .player import Player
from .draw import DrawBest

FISH = 0
LXNS = 1


async def compress_png(fp, output, force=True, quality=None):
    """
    Compresses a PNG file asynchronously.

    Args:
        fp (str): The file path of the original PNG file.
        output (str): The file path for the compressed PNG file.
        force (bool, optional): Whether to force compression. Defaults to True.
        quality (int or str, optional): Compression quality parameter. Defaults to None.

    Returns:
        float: Compression ratio percentage.
    """
    if not os.path.exists(fp):
        raise FileNotFoundError(f"File not found: {fp}")

    force_command = "-f" if force else ""
    quality_command = ""

    if quality and isinstance(quality, int):
        quality_command = f"--quality {quality}"
    if quality and isinstance(quality, str):
        quality_command = f"--quality {quality}"

    command = (
        f"pngquant {fp} "
        f"--skip-if-larger {force_command} "
        f"{quality_command} "
        f"--output {output}"
    )

    try:
        process = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        # 获取原始图像大小
        original_size = os.path.getsize(fp)

        # 获取压缩后文件的大小
        compressed_size = os.path.getsize(output)

        # 计算压缩比
        compression_ratio = (1 - compressed_size / original_size) * 100

        # 检查命令是否成功执行
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command)

        return compression_ratio
    except asyncio.CancelledError as exc:
        raise exc from None
    except Exception as e:
        raise RuntimeError(f"An error occurred: {e}") from e


async def handle_bind(message: Message):
    user_id = int(message.author.id)
    content = message.content.split("/bind")[1].strip()
    if not content:
        await message.reply(
            content="""
            这里是bind指令的说明：
            /bind后面可以接上水鱼查分器的用户名或者是落雪咖啡屋绑定的QQ号。
            例如：/bind user 将绑定用户名 user。

            如果要强制指定平台，可以在用户名后面加上空格：
            - f 表示水鱼查分器
            - l 表示落雪咖啡屋

            例如：/bind user f 将绑定用户名到水鱼查分器。
            默认情况下会自动判断平台。

            Tip: 输入 / 可以快速唤起我。如有问题请联系频道主。
            """
        )
        return

    # 获取用户名和平台信息
    content_list = content.split(" ")
    user_name = content_list[0]

    # 默认为水鱼查分器
    platform_id = FISH

    # 如果输入了平台参数，则判断平台
    if len(content_list) > 1:
        platform_arg = content_list[1]
        if platform_arg.startswith("l"):
            platform_id = LXNS
        else:
            platform_id = FISH
    else:
        # 根据用户名自动判断平台
        if not is_fish_else_lxns(user_name):
            platform_id = LXNS

    # 绑定用户
    try:
        add_or_update_user(user_id, user_name, platform_id)
    except DatabaseOperationError as e:
        logger.error(f"绑定用户时出错: {e}")
        await message.reply(content="绑定失败，数据库操作出错。请稍后再试。")
        return

    platform_str = ["水鱼查分器", "落雪咖啡屋"]
    await message.reply(
        content=f"[{user_name}] 已经成功绑定到你的频道号了！查分平台为 [{platform_str[platform_id]}]。"
    )


async def handle_b50(message: Message):
    start_time = time.time()
    user_id = int(message.author.id)
    try:
        username, platform_id, score = get_user_by_id(user_id)
    except UserNotFoundError:
        await message.reply(content="请先使用 /bind 指令绑定你的查分器账号。")
        return
    except DatabaseOperationError as e:
        logger.error(f"查询用户时出错: {e}")
        await message.reply(content="查询失败, Bot出现了问题。请稍后再试。")
        return

    player = Player(
        username,
        user_id,
        avatar_url=message.author.avatar,
        api_secret=LXNS_API_SECRET,
    )

    try:
        if platform_id == FISH:
            logger.info(f"用户 {user_id} 使用水鱼查分器")
            await player.fetch_divingfish()
        elif platform_id == LXNS:
            logger.info(f"用户 {user_id} 使用落雪咖啡屋")
            await player.fetch_luoxue()
    except Exception as e:
        logger.error(f"获取查分器数据时出错: {e}")
        await message.reply(
            content=f"获取数据时出错，请检查查分器网站的隐私设置，如果进一步遇到问题，请联系频道主。\n 查分器平台: {'水鱼查分器' if platform_id == FISH else '落雪咖啡屋'} 用户名: {username}"
        )
        return

    try:
        drawBest = DrawBest(player)
        draw = await drawBest.draw()

        # Save the image to a file
        if not os.path.exists("./tmp"):
            os.makedirs("./tmp")
        image_path = f"./tmp/{username}_b50.png"
        draw.save(image_path)

        # Compress the image
        compressed_image_path = f"./tmp/{username}_b50_compressed.png"
        compression_ratio = await compress_png(image_path, compressed_image_path)

    except Exception as e:
        logger.error(f"绘制或压缩图片时出错: {e}")
        await message.reply(content="处理图片时出错，请稍后再试。")
        return

    try:
        update_user_score(user_id, player.rating)
    except DatabaseOperationError as e:
        logger.error(f"更新用户时出错: {e}")
        return

    generation_time = time.time() - start_time

    await message.reply(
        file_image=compressed_image_path,  # Pass the compressed file path
    )
    await message.reply(
        content=f"@{message.author.username} B50生成成功, 耗时 {generation_time:.2f} 秒。\n压缩比: {compression_ratio:.2f}%\n更多统计信息可以访问 Maimai的网页查分器(详见频道帖子-相关教程)。",
    )


# 定义支持的指令及其处理函数（指令名应为小写）
COMMANDS = {
    "bind": handle_bind,
    "b50": handle_b50,
}

# 默认大写的插件名
COMMAND_NAME = "B50"
