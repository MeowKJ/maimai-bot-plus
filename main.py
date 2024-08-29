import os
import botpy
from botpy.logging import DEFAULT_FILE_HANDLER
from src.bot import MyClient

from config import DEBUG, BOT_APPID, BOT_SECRET


def main():

    # 设置 bot 的 intents
    intents = botpy.Intents(public_guild_messages=True, public_messages=True)

    # 设置Bot日志文件路径
    DEFAULT_FILE_HANDLER["filename"] = os.path.join(os.getcwd(), "bot.log")

    # 创建并配置客户端
    client = MyClient(
        intents=intents,
        is_sandbox=DEBUG,
        timeout=20,
        ext_handlers=DEFAULT_FILE_HANDLER,
    )

    # Bot 启动
    client.run(appid=BOT_APPID, secret=BOT_SECRET)


if __name__ == "__main__":
    main()
