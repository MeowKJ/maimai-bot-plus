import os
import time
import random
from botpy.message import Message
from botpy.types.message import Reference

from config import LXNS_API_SECRET, DEBUG
from src.libraries.database import (
    add_or_update_user,
    get_user_by_id,
    update_user_score,
    update_user_favorite,
)
from src.libraries.database.exceptions import DatabaseOperationError, UserNotFoundError

from src.libraries.assets.get import assets, AssetType

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
        content = (
            "📖 绑定指令使用说明:\n\n"
            "使用 `/bind` 指令可以绑定水鱼查分器的用户名或落雪咖啡屋绑定的 QQ 号。\n\n"
            "👤 基本用法:\n"
            "- `/bind 你的用户名` - 绑定你的用户名（水鱼）或 QQ 号（落雪）。\n"
            "  例如：`/bind xxx`\n\n"
            "⚙️ 自动判断:\n"
            "默认情况下，系统会自动判断平台。\n\n"
            "🌐 指定平台（仅在自动识别错误的情况下）:\n"
            "- 在用户名后加一个空格并添加平台标识：\n"
            "  - `f` 表示水鱼查分器\n"
            "  - `l` 表示落雪咖啡屋\n"
            "  例如：`/bind xxx f` 将用户名 xxx 强制指定到水鱼查分器。\n\n"
            "💡 小提示:\n"
            "输入 `/` 可以快速唤起我。如果遇到问题，请联系频道主。"
        )

        # 8 分之一的概率显示隐藏内容
        if random.randint(1, 8) == 1:
            content += (
                "\n\n🎀 绑定喜欢的音击小女孩!（隐藏功能）:\n"
                "- 输入 `/bind @OngekiGirls show` 可以查看音击小女孩列表。\n"
                "- 输入 `/bind @OngekiGirls 序号` 可以绑定你喜欢的音击小女孩。\n"
                "  例如：`/bind @OngekiGirls 1`\n"
                "序号0为不绑定, 序号1-17为对应的音击小女孩。\n"
                "绑定的小女孩将会在你的 B50 中出现哦~"
            )

        await message.reply(content=content)
        return

    # 获取用户名和平台信息
    content_list = content.split(" ")
    user_name = content_list[0]

    print(content_list)
    print(user_name)
    # 如果是绑定音击小女孩
    if user_name == "@OngekiGirls" and len(content_list) > 1:

        args = content_list[1]
        logger.info(f"[BIND]用户 {user_id} 尝试绑定音击小女孩: {args}")

        if args == "show":
            await message.reply(
                file_image=await assets.get_async(AssetType.ONGEKI, "OngekiGirls.png")
            )
            return

        try:
            girl_number = float(args)

            # 检查是否为整数且在 0 到 17 之间
            if girl_number.is_integer() and 0 <= int(girl_number) <= 17:
                girl_number = int(girl_number)
                try:
                    update_user_favorite(user_id, girl_number)
                    await message.reply(
                        content=f"🎉 已成功绑定音击小女孩 {girl_number}!",
                        message_reference=message_reference,
                    )
                except Exception as e:
                    logger.error(f"绑定音击小女孩时出错: {e}")
                    await message.reply(
                        content="❌ 绑定失败, 首先需要绑定查分器。",
                        message_reference=message_reference,
                    )
            else:
                await message.reply(
                    content="❌ 输入的数字无效，请输入 1 到 17 之间的整数。",
                    message_reference=message_reference,
                )
        except ValueError:
            await message.reply(
                content="❌ 请输入一个有效的整数。",
                message_reference=message_reference,
            )
        return

    # 绑定音击小女孩结束

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
            content="❌ 绑定失败，由于数据库操作出错，请稍后再试。",
            message_reference=message_reference,
        )

        return

    # 成功绑定后回复用户
    await message.reply(
        content=(
            f"🎉 [{user_name}] 已成功绑定到你的频道号！\n"
            f"✅ 查分平台: [{PLATFORM_STR[platform_id]}]\n"
            "📊 你可以使用 /b50 指令来查分。\n"
            "⏳ 提示: 初次查分时, 可能需要稍作等待, 因为bot需要下载缺失的资源。"
        ),
        message_reference=message_reference,
    )


# 处理 /b50 指令的异步函数
async def handle_b50(message: Message):
    message_reference = Reference(message_id=message.id)
    start_time = time.time()
    user_id = int(message.author.id)

    # 尝试从数据库获取用户信息
    try:
        username, platform_id, score, favorite_id = get_user_by_id(user_id)
    except Exception:
        await message.reply(
            content=(
                "⚠️ 查分失败：你尚未绑定查分器账号。\n"
                "请使用 /bind 指令绑定你的查分器账号，然后再尝试查分。\n"
            ),
            message_reference=message_reference,
        )
        return
    # 初始化玩家对象
    player = Player(
        username,
        user_id,
        favorite_id=favorite_id,
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
                "⚠️ 获取数据时出错，请检查以下事项：\n"
                "1.确认用户名或QQ号是否正确输入。\n"
                "2.检查查分网站隐私设置，确保查分器有权限访问你的数据。\n"
                "3.尝试重新操作几次。\n"
                "如果问题仍然存在，请联系频道主寻求帮助。\n\n"
                f"当前查分器平台: {PLATFORM_STR[platform_id]}\n"
                f"用户名: {username}"
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

        # 如果是调试模式，不压缩图片
        if not DEBUG:
            compression_ratio = await compress_png(image_path, compressed_image_path)
        else:
            draw.show()
            compression_ratio = 0
            compressed_image_path = image_path

    except Exception as e:
        logger.error(f"绘制或压缩图片时出错: {e}")
        await message.reply(
            content=(
                "⚠️ 处理图片时出错, 可能是bot被玩坏了。\n"
                "如果这个问题持续出现，请联系频道主以获得帮助。"
            ),
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
    )

    # 回复生成成功信息
    if generation_time <= 3:
        time_message = "哇，一下子就查完了呢！\n"
    elif generation_time <= 20:
        time_message = ""
    elif generation_time <= 45:
        time_message = "你的 B50 中有些冷门歌曲了, 所以 bot 下载了一些资源喵~\n"
    elif generation_time <= 75:
        time_message = (
            "你的 B50 中有比较多的冷门歌曲, bot 下载了一些资源以确保完整性喵~\n"
        )
    else:
        time_message = (
            "你的 B50 中包含了很多冷门歌曲, bot 需要花费较长时间下载资源喵~\n"
        )

    await message.reply(
        content=(
            f"🎉 B50[{PLATFORM_STR[platform_id]}] 生成成功啦，耗时 {generation_time:.2f} 喵！\n"
            f"📉 压缩比: {compression_ratio:.2f}%\n"
            f"{time_message}"
            "更多有趣的统计信息可以去 Maimai 的网页查分器查看-参见频道帖子中的相关教程\n"
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
