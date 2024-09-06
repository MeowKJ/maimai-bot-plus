from botpy.message import Message, GroupMessage
from botpy.types.message import Reference
from botpy import logger
from src.libraries.common.file.upload import upload_to_image_server
from config import DEFAULT_AVATAR_URL


class MixMessage:
    user_id: str
    group_message: GroupMessage
    guild_message: Message
    message_type: str
    message_reference: Reference
    message_seq_id: int = 0
    avatar_url: str = ""

    def __init__(self, message: GroupMessage | Message) -> None:
        """初始化 MixMessage 类，根据消息类型设置相应的属性。

        Args:
            message (GroupMessage | Message): 接收到的消息对象，可能是群消息或频道消息。
        """
        self.message_reference = Reference(message_id=message.id)
        if isinstance(message, GroupMessage):
            self.group_message = message
            self.user_id = message.author.member_openid
            self.avatar_url = DEFAULT_AVATAR_URL
            self.message_type = "group"
        else:
            self.guild_message = message
            self.user_id = message.author.id
            self.avatar_url = message.author.avatar
            self.message_type = "guild"

    async def reply(
        self, content: str = "", file_image: str = "", use_reference: bool = False
    ) -> None:
        """回复消息，可以选择性地附带图片或使用消息引用。

        Args:
            content (str, optional): 回复的文本内容。默认为空字符串。
            file_image (str, optional): 要发送的图片文件路径。默认为空字符串。
            use_reference (bool, optional): 是否使用消息引用进行回复。默认为 False。
        """
        if self.message_type == "guild":
            if use_reference:
                await self.guild_message.reply(
                    content=content,
                    message_reference=self.message_reference,
                )
            else:
                await self.guild_message.reply(content=content, file_image=file_image)
        elif self.message_type == "group":
            if file_image:
                image_url = await upload_to_image_server(file_image)
                logger.info(f"Upload image to SERVER: {image_url}")
                # 上传图片的URL到群文件管理
                upload_media = await self.group_message._api.post_group_file(
                    group_openid=self.group_message.group_openid,
                    file_type=1,
                    url=image_url,
                    srv_send_msg=False,
                )

                # 发送富媒体消息
                await self.group_message._api.post_group_message(
                    group_openid=self.group_message.group_openid,
                    msg_type=7,  # 7表示富媒体类型
                    msg_id=self.group_message.id,
                    media=upload_media,
                    msg_seq=self.message_seq_id,
                    content=content,
                )
            else:
                await self.group_message._api.post_group_message(
                    group_openid=self.group_message.group_openid,
                    msg_id=self.group_message.id,
                    msg_seq=self.message_seq_id,
                    content=content,
                )
            # 将消息序号加1
            self.message_seq_id += 1

    def get_args(self, command: str = "", part_index: int = 1) -> str:
        """获取命令参数，如果未找到命令则返回原始消息内容。

        Args:
            command (str, optional): 要查找的命令字符串。默认为空字符串。
            part_index (int, optional): 拆分后的消息部分索引。默认为1。

        Returns:
            str: 返回命令后的参数或原始消息内容。
        """
        if self.message_type == "group":
            message_content = self.group_message.content
        elif self.message_type == "guild":
            message_content = self.guild_message.content
        else:
            return ""

        if command and command in message_content:
            return message_content.split(command, maxsplit=1)[part_index].strip()
        return message_content.strip()
