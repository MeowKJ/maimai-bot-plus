import os
import importlib
import logging

from botpy import Client
from botpy.message import Message

from botpy import logger


class MyClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commands = {}
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
                        self.commands.update(
                            {
                                cmd_name.lower(): cmd_func
                                for cmd_name, cmd_func in command_module.COMMANDS.items()
                            }
                        )
                        logger.info(
                            f"[BOT] Loaded commands from module '{module_name}': {', '.join(command_module.COMMANDS.keys())}."
                        )
                except Exception as e:
                    logger.error(f"[BOT] Error loading module '{module_name}': {e}")

    async def on_at_message_create(self, message: Message):
        logger.info(
            f"[BOT] Received message: {message.author.username}: {message.content}"
        )
        content = message.content.split(">")[1].strip()

        if content.startswith("/"):
            command = content.split()[0][1:].lower()  # 提取指令名并转换为小写
            if command in self.commands:
                await self.commands[command](message)
            else:
                await message.reply(content=f"未知的指令: {command}")
