import os
import asyncio
import random
import tempfile
from collections import Counter

import aiohttp
import time

from PIL import Image
from botpy import Client
from botpy.message import GroupMessage
from src.libraries.assets.get import assets, AssetType
from .tools import (
    get_alias_by_id,
    get_version_name,
    upload_to_imagekit,
    translate_to_chinese,
)

from botpy import logger

# 用于存储每个群的游戏状态
group_game_state = {}


class GuessSongHandler:
    """
    处理猜歌游戏的类，每个群组同时只能运行一个游戏实例。
    """

    def __init__(self, message: GroupMessage):
        self.message_seq_id = 1
        self.message = message
        self.group_id = message.group_openid  # 使用 group_openid 作为唯一标识
        self.temp_files = []
        self.current_song = None
        self.alias = []
        self.game_active = False
        self.possible_answers = []

    async def start_game(self, args):
        """
        开始猜歌游戏。
        """
        try:
            if (
                self.group_id in group_game_state
                and group_game_state[self.group_id].game_active
            ):
                await self.send_message(
                    "😅 已有一个游戏正在进行中！请等待当前游戏结束。"
                )
                return

            self.game_active = True
            group_game_state[self.group_id] = self  # 将实例保存到全局状态字典中

            while len(self.alias) < 3:
                self.current_song = await self.choice_song(args)
                if not self.current_song:
                    await self.send_message("❌ 无法获取歌曲列表，请稍后再试。")
                    self.game_active = False
                    del group_game_state[self.group_id]
                    return
                self.alias = await get_alias_by_id(self.current_song["id"])
                cover_path = await self.get_cover()
                logger.info(f"Chosen song: {self.current_song['title']}")

            title = self.current_song["title"].replace(" ", "").lower()

            chinese = await translate_to_chinese(self.current_song["title"], "en")
            chinese2 = await translate_to_chinese(self.current_song["title"], "ja")

            self.possible_answers = [title, chinese, chinese2] + self.alias
            logger.info(f"Possible answers: {self.possible_answers}")

            await self.send_message("🎵 开始猜歌吧！这是什么乐曲呢？", image=cover_path)
            await self.wait_for_guess()
        except Exception as e:
            logger.error(f"Error starting game: {str(e)}")
            await self.end_game("❌ 游戏出现了一个错误，已结束。")

    async def send_message(self, content, image=None):
        """
        发送消息到群组或频道。支持发送文本和图片。
        """
        try:
            if image:
                # 上传图片到 ImageKit 并获取URL
                image_url = await upload_to_imagekit(image)
                # image_url = image
                if not image_url:
                    await self.message.reply(content="图片上传失败，请稍后再试。")
                    self.end_game()
                    return

                # 上传图片的URL到群文件管理
                upload_media = await self.message._api.post_group_file(
                    group_openid=self.group_id,
                    file_type=1,
                    url=image_url,
                    srv_send_msg=False,
                )

                # 发送富媒体消息
                await self.message._api.post_group_message(
                    group_openid=self.group_id,
                    msg_type=7,  # 7表示富媒体类型
                    msg_id=self.message.id,
                    media=upload_media,
                    msg_seq=self.message_seq_id,
                    content=content,
                )
            else:
                # 发送普通文本消息
                await self.message._api.post_group_message(
                    group_openid=self.group_id,
                    content=content,
                    msg_type=0,  # 0表示文本类型
                    msg_id=self.message.id,
                    msg_seq=self.message_seq_id,
                )
            self.message_seq_id += 1
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            await self.end_game(is_message=False)

    async def guess_song(self, message: GroupMessage):
        """
        处理用户的猜歌尝试。
        """

        if not self.game_active:
            return
        # 转移消息对象
        self.message = message

        try:
            if await self.judge_guess(message.content):
                await self.send_message("🎉 恭喜你，猜对了！积分+1")
                await self.end_game("", True)
            else:
                await self.send_message("❌ 猜错了，再试试吧！")
        except Exception as e:
            logger.error(f"Error during guessing: {str(e)}")
            await self.end_game("❌ 游戏在猜测环节出现程序上的错误，已结束。")

    async def judge_guess(self, msg):
        """
        判断用户的猜测是否正确。
        用户猜测需要与歌曲的标题或别名有至少 20% 的连续字符匹配才被认为是正确的，空格不计入字符中。
        """
        if not msg:
            return False

        guess_lower = msg.replace(" ", "").lower()
        for answer in self.possible_answers:
            if not answer:
                if not self.current_song["title"].replace(" ", ""):
                    return True
            if self.get_max_match_length(guess_lower, answer) / len(answer) >= 0.3:
                return True
        return False

    def get_max_match_length(self, guess, answer):
        """
        获取 guess 在 answer 中的最长连续匹配长度。
        """
        max_length = 0
        for i in range(len(answer)):
            for j in range(i + 1, len(answer) + 1):
                if guess.find(answer[i:j]) != -1:
                    max_length = max(max_length, j - i)
        return max_length

    async def wait_for_guess(self):
        """
        等待玩家猜测，或直到时间结束。
        提供不同的提示信息。
        """
        try:
            await asyncio.sleep(10)  # 等待 10 秒
            if self.game_active:
                await self.provide_hint("genre or version or artist")
                await asyncio.sleep(15)  # 再等待 10 秒
            else:
                return

            if self.game_active:
                await self.provide_hint("difficulty level")
                await asyncio.sleep(15)  # 再等待 10 秒
            else:
                return

            if self.game_active:
                await self.provide_hint("title")
                await asyncio.sleep(15)
            else:
                return

            if self.game_active:
                await self.provide_hint("cover image")
                await asyncio.sleep(20)  # 再等待 10 秒
            else:
                return

            if self.game_active:
                await self.provide_hint("alias")
                await asyncio.sleep(25)
            else:
                return

            if self.game_active:
                await self.end_game(be_guessed=False)
            else:
                return

        except Exception as e:
            logger.error(f"Error during waiting for guess: {str(e)}")
            await self.end_game("❌ 游戏出现错误，已结束。")

    async def provide_hint(self, hint_type):
        """
        根据提示类型提供相应的提示。
        """
        try:
            if hint_type == "genre or version or artist":
                hint_options = [
                    {"name": "分类", "value": self.current_song["genre"]},
                    {
                        "name": "版本",
                        "value": get_version_name(self.current_song["version"]),
                    },
                    {"name": "艺术家", "value": self.current_song["artist"]},
                    {"name": "BPM", "value": str(self.current_song["bpm"])},
                ]
                hint_info = random.choice(hint_options)
                await self.send_message(
                    f"🔍 提示1: {hint_info['name']}是 {hint_info['value']}"
                )

            elif hint_type == "difficulty level":
                difficulties = []
                if self.current_song["difficulties"]["dx"]:
                    difficulties.append(self.current_song["difficulties"]["dx"])
                if self.current_song["difficulties"]["standard"]:
                    difficulties.append(self.current_song["difficulties"]["standard"])
                if difficulties:
                    chosen_difficulty = random.choice(difficulties)
                    hint_list = [
                        f"🔍 提示2: Master难度等级为 {chosen_difficulty[3]['level']}",
                        f"🔍 提示2: Master谱师是 {chosen_difficulty[3]['note_designer']}",
                    ]
                    await self.send_message(random.choice(hint_list))

            elif hint_type == "cover image":
                cover_path = await self.get_cover(120, 120)
                await self.send_message("🔍 提示4: 更大的曲绘来了！", image=cover_path)

            elif hint_type == "title":
                await self.send_message(
                    f"🔍 提示3: 歌曲名的第一个字母是 {self.current_song['title'][0]}"
                )

            elif hint_type == "alias":
                if self.alias:
                    if len(self.alias) > 5:
                        one_alias = random.choice(self.alias)
                        if one_alias:
                            self.alias.remove(one_alias)
                            await self.send_message(
                                f"🔍 提示5: 有人称这首歌为 {one_alias}"
                            )
                            return
                await self.send_message(
                    f"\n🔍 提示5:\n"
                    f"分类({self.current_song['genre']}\n"
                    f"艺术家({self.current_song['artist']})\n"
                    f"BPM({self.current_song['bpm']})"
                )
        except Exception as e:
            logger.error(f"Error providing hint: {str(e)}")
            await self.end_game("❌ 提供提示时出错，游戏结束。")

    async def end_game(self, reason="", is_message=True, be_guessed=True):
        """
        结束游戏，并公布正确答案。
        """
        self.game_active = False

        try:
            # 清理临时文件
            for temp_file in self.temp_files:
                try:
                    os.remove(temp_file)
                except OSError:
                    pass
            self.temp_files.clear()
            if is_message:
                cover = await assets.get_async(AssetType.COVER, self.current_song["id"])
                if be_guessed:
                    await self.send_message(
                        f"🎉 🎉 🎉 {self.current_song['title']}！{reason}",
                        image=cover,
                    )
                else:
                    await self.send_message(
                        f"没有人猜对！正确答案是 {self.current_song['title']}。{reason}",
                        image=cover,
                    )
            self.current_song = None
        except Exception as e:
            logger.error(f"Error ending game: {str(e)}")
        finally:
            # 移除群组的游戏状态
            if self.group_id in group_game_state:
                del group_game_state[self.group_id]

    @staticmethod
    async def choice_song(categories=[]):
        """
        从曲目列表随机选择一首歌，根据提供的分类。
        """
        genre_dict = {
            "0": "maimai",
            "1": "POPSアニメ",
            "2": "niconicoボーカロイド",
            "3": "ゲームバラエティ",
            "4": "オンゲキCHUNITHM",
            "5": "東方Project",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://maimai.lxns.net/api/v0/maimai/song/list"
                ) as resp:
                    if resp.status != 200:
                        logger.error(f"Error fetching song list: {resp.status}")
                        return None

                    data = await resp.json()
                    songs = data.get("songs", [])

                    if not categories:
                        # 如果 categories 是空的，随机选择所有歌曲
                        return random.choice(songs) if songs else None

                    # 根据 categories 筛选歌曲
                    genre_filter = set(
                        genre_dict.get(cat) for cat in categories if cat in genre_dict
                    )

                    song_list = [
                        song for song in songs if song["genre"] in genre_filter
                    ]

                    return random.choice(song_list) if song_list else None

        except Exception as e:
            logger.error(f"Error choosing song: {str(e)}")
            return None

    async def get_cover(self, length=70, width=70):
        """
        获取歌曲封面的一部分。如果95%的像素都是同一种颜色，则重新生成。
        """
        try:
            cover = await assets.get_async(AssetType.COVER, self.current_song["id"])

            with Image.open(cover) as img:
                for _ in range(5):
                    x = random.randint(0, img.width - length)
                    y = random.randint(0, img.height - width)
                    crop_area = (x, y, x + length, y + width)
                    cropped_img = img.crop(crop_area)

                    color_counts = Counter(cropped_img.getdata())
                    most_common_color_count = color_counts.most_common(1)[0][1]

                    if most_common_color_count / (length * width) < 0.95:
                        temp_file = tempfile.mktemp(
                            suffix=f"_{int(time.time())}_crop.png"
                        )
                        cropped_img.save(temp_file)
                        self.temp_files.append(temp_file)
                        return temp_file

                temp_file = tempfile.mktemp(suffix=f"_{int(time.time())}_crop.png")
                cropped_img.save(temp_file)
                self.temp_files.append(temp_file)
                return temp_file
        except Exception as e:
            logger.error(f"Error generating cover image: {str(e)}")
            await self.end_game("❌ 获取封面时出错，游戏结束。")
            return None


async def guess(message: GroupMessage):
    logger.info(f"Received guess command from {message.author.member_openid}")
    msg = message.content.strip().lower()
    args = msg.split(" ")
    categories = args[1] if len(args) > 1 else ""

    help_content = (
        "🎵 猜歌游戏指令帮助\n\n"
        "👋 基本指令：\n"
        "- /guess help - 获取帮助信息\n\n"
        "🎶 开始游戏：\n"
        "- /guess - 随机开始一个包含所有歌曲的猜歌游戏\n"
        "- /guess 0 - 使用 Maimai 分类的歌曲开始游戏\n"
        "- /guess 1 - 使用 流行动漫 分类的歌曲开始游戏\n"
        "- /guess 2 - 使用 niconico & Vocaloid 分类的歌曲开始游戏\n"
        "- /guess 3 - 使用 其他游戏 分类的歌曲开始游戏\n"
        "- /guess 4 - 使用 音击中二 分类的歌曲开始游戏\n"
        "- /guess 5 - 使用 东方Project 分类的歌曲开始游戏\n"
        "- 组合分类：可以直接使用多个分类字符，例如 /guess 012\n\n"
        "🚫 结束游戏：\n"
        "- 不玩了 - 结束当前游戏"
    )

    category_names = {
        "0": "Maimai",
        "1": "流行动漫",
        "2": "niconico & Vocaloid",
        "3": "其他游戏",
        "4": "音击中二",
        "5": "东方Project",
    }

    if "help" in categories:
        await message.reply(content=help_content)
        return

    # 筛选有效的分类字符，并去重
    valid_categories = list(
        dict.fromkeys(
            category_names.get(cat) for cat in categories if cat in category_names
        )
    )

    if not valid_categories and categories:
        await message.reply(
            content="❌ 请指定有效的分类或使用 /guess help 获取帮助信息"
        )
        return

    if valid_categories:
        if len(valid_categories) == 1:
            response = f"🎵 选择分类{valid_categories[0]}的歌曲开始猜歌游戏"
        else:
            response = f"🎵 选择分类{' 和 '.join(valid_categories)}的歌曲开始猜歌游戏"
    else:
        response = "🎵 随机开始一个包含所有歌曲的猜歌游戏"

    await message.reply(content=response)

    handler = GuessSongHandler(message=message)
    await handler.start_game(categories)


# 默认处理未匹配指令的函数
async def handle_unknown_command(message: GroupMessage):
    logger.info(f"Us: {message.content}")
    group_id = message.group_openid
    if group_id in group_game_state:
        await group_game_state[group_id].guess_song(message)
        return True
    return False


# 定义支持的指令及其处理函数（指令名应为小写）
COMMANDS = {
    "guess": guess,
}

# 指令范围
COMMAND_SCOPE = "group"

# 设置默认处理函数
DEFAULT_HANDLER = handle_unknown_command
