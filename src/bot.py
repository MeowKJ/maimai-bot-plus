import os
import importlib

from botpy import Client
from botpy.message import Message, GroupMessage

from botpy import logger


class MyClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_commands = {}  # 存储频道指令
        self.group_commands = {}  # 存储群指令
        self.default_channel_handlers = []  # 默认频道处理函数列表
        self.default_group_handlers = []  # 默认群处理函数列表
        self.load_plugins()

    async def on_ready(self):
        logger.info("[BOT] robot 「%s」 准备好了!", self.robot.name)

    def load_plugins(self):
        plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
        for module_name in os.listdir(plugins_dir):
            module_path = os.path.join(plugins_dir, module_name)
            if os.path.isdir(module_path):
                try:
                    command_module = importlib.import_module(
                        f"src.plugins.{module_name}.command"
                    )
                    if hasattr(command_module, "COMMANDS"):
                        for cmd_name, cmd_func in command_module.COMMANDS.items():
                            cmd_name_lower = cmd_name.lower()
                            if command_module.COMMAND_SCOPE in ["channel", "both"]:
                                self.channel_commands[cmd_name_lower] = cmd_func
                            if command_module.COMMAND_SCOPE in ["group", "both"]:
                                self.group_commands[cmd_name_lower] = cmd_func

                        logger.info(
                            f"[BOT] Loaded commands from module '{module_name}': {', '.join(command_module.COMMANDS.keys())}."
                        )

                    # 加载未匹配指令的处理函数
                    if hasattr(command_module, "DEFAULT_HANDLER"):
                        if command_module.COMMAND_SCOPE in ["channel", "both"]:
                            self.default_channel_handlers.append(
                                command_module.DEFAULT_HANDLER
                            )
                        if command_module.COMMAND_SCOPE in ["group", "both"]:
                            self.default_group_handlers.append(
                                command_module.DEFAULT_HANDLER
                            )

                except Exception as e:
                    # 打印跟踪报错文件具体位置
                    logger.error(
                        f"[BOT] Error loading module '{module_name}': {e} in {module_path}"
                    )

    async def on_at_message_create(self, message: Message):
        logger.info(
            f"[BOT] Received message: {message.author.username}: {message.content}"
        )
        content = message.content.split(">", maxsplit=1)[1].strip()

        if content.startswith("/"):
            command = content.split()[0][1:].lower()
            if command in self.channel_commands:
                await self.channel_commands[command](message)
        else:
            await self.handle_unmatched_channel_command(message)

    async def on_group_at_message_create(self, message: GroupMessage):
        logger.info(
            f"[BOT] Received group message: {message.author.member_openid}: {message.content}"
        )
        content = message.content.strip()

        if content.startswith("/"):
            command = content.split()[0][1:].lower()
            if command in self.group_commands:
                await self.group_commands[command](message)
        else:
            await self.handle_unmatched_group_command(message)

    async def handle_unmatched_channel_command(self, message):
        for handler in self.default_channel_handlers:
            if await handler(message):
                return  # 如果某个处理函数成功处理了消息，则退出

    async def handle_unmatched_group_command(self, message):
        for handler in self.default_group_handlers:
            if await handler(message):
                return  # 如果某个处理函数成功处理了消息，则退出
