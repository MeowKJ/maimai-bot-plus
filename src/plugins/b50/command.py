import os
import time
from botpy.message import Message
from botpy.types.message import Reference

from config import LXNS_API_SECRET
from src.libraries.database import add_or_update_user, get_user_by_id, update_user_score
from src.libraries.database.exceptions import DatabaseOperationError, UserNotFoundError

from .tools import is_fish_else_lxns, compress_png
from .player import Player
from .draw import DrawBest

from botpy import logger

# 定义查分平台的常量
FISH = 0
LXNS = 1
PLATFORM_STR = ["水鱼查分器", "落雪咖啡屋"]


# 处理 /bind 指令的异步函数
async def handle_bind(message: Message):
    message_reference = Reference(message_id=message.id)

    user_id = int(message.author.id)
    content = message.content.split("/bind", 1)[-1].strip()

    # 如果用户没有提供绑定信息，返回绑定说明
    if not content:
        await message.reply(
            content=(
                "这里是bind指令的说明:\n"
                "/bind后面可以接上水鱼查分器的用户名或者是落雪咖啡屋绑定的QQ号。\n"
                "例如：/bind user 将绑定用户名 user。\n\n"
                "如果要强制指定平台，可以在用户名后面加上空格：\n"
                "- f 表示水鱼查分器\n"
                "- l 表示落雪咖啡屋\n\n"
                "例如：/bind user f 将绑定用户名到水鱼查分器。\n"
                "默认情况下会自动判断平台。\n\n"
                "Tip: 输入 / 可以快速唤起我。如有问题请联系频道主。"
            )
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

    # 尝试绑定用户到数据库
    try:
        add_or_update_user(user_id, user_name, platform_id)
    except DatabaseOperationError as e:
        logger.error(f"绑定用户时出错: {e}")
        await message.reply(
            content="绑定失败，数据库操作出错。请稍后再试。",
            message_reference=message_reference,
        )
        return

    # 成功绑定后回复用户
    await message.reply(
        content=f"[{user_name}] 已经成功绑定到你的频道号了！查分平台为 [{PLATFORM_STR[platform_id]}]。",
        message_reference=message_reference,
    )


# 处理 /b50 指令的异步函数
async def handle_b50(message: Message):
    message_reference = Reference(message_id=message.id)
    start_time = time.time()
    user_id = int(message.author.id)

    # 尝试从数据库获取用户信息
    try:
        username, platform_id, score = get_user_by_id(user_id)
    except Exception:
        await message.reply(
            content="请先使用 /bind 指令绑定你的查分器账号。",
            message_reference=message_reference,
        )
        return

    # 初始化玩家对象
    player = Player(
        username,
        user_id,
        avatar_url=message.author.avatar,
        api_secret=LXNS_API_SECRET,
    )

    # 获取查分器数据
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
            content=(
                "获取数据时出错, 请检查以下事项：\n"
                "1. 用户名是否填错了\n"
                "2. 网站的隐私设置，是否允许查分器访问\n"
                "3. 重试几次\n"
                "如果进一步遇到问题，请联系频道主。\n\n"
                f"查分器平台: {PLATFORM_STR[platform_id]} 用户名: {username}"
            ),
            message_reference=message_reference,
        )
        return

    # 绘制和压缩图片
    try:
        drawBest = DrawBest(player)
        draw = await drawBest.draw()

        # 保存图片到文件
        if not os.path.exists("./tmp"):
            os.makedirs("./tmp")
        image_path = f"./tmp/{username}_b50.png"
        draw.save(image_path)

        # 压缩图片
        compressed_image_path = f"./tmp/{username}_b50_compressed.png"
        compression_ratio = await compress_png(image_path, compressed_image_path)

    except Exception as e:
        logger.error(f"绘制或压缩图片时出错: {e}")
        await message.reply(
            content="处理图片时出错, 如果多次出现错误, 请联系频道主。",
            message_reference=message_reference,
        )
        return

    # 更新用户分数到数据库
    try:
        update_user_score(user_id, player.rating)
    except DatabaseOperationError as e:
        logger.error(f"更新用户时出错: {e}")
        return

    # 计算生成时间
    generation_time = time.time() - start_time

    # 回复压缩后的图片
    await message.reply(
        file_image=compressed_image_path,
        message_reference=message_reference,
    )

    # 回复生成成功信息
    await message.reply(
        content=(
            f"B50[{PLATFORM_STR[platform_id]}]生成成功, 耗时 {generation_time:.2f} 秒。\n"
            f"压缩比: {compression_ratio:.2f}%\n"
            "更多统计信息可以访问 Maimai的网页查分器 (详见频道帖子-相关教程)。"
        ),
        message_reference=message_reference,
    )


# 空操作函数，用于处理无效指令
async def do_nothing(message: Message):
    pass


# 定义支持的指令及其处理函数（指令名应为小写）
COMMANDS = {
    "bind": handle_bind,
    "b50": handle_b50,
    "bindo": do_nothing,
    "b50o": do_nothing,
}

# 默认大写的插件名
COMMAND_NAME = "B50"
