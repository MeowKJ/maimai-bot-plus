# plugins/test/command.py


async def handle_hello(message):
    await message.reply(content="Hello!")


# 定义支持的指令及其处理函数（指令名应为小写）
COMMANDS = {
    "hello": handle_hello,
}

# 默认大写的插件名
COMMAND_NAME = "TEST"
