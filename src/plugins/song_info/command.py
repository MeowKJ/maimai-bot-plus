import time
import aiohttp
from typing import List, Dict, Any
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from botpy.message import GroupMessage, Message
from botpy import logger

from src.libraries.common.message.message import MixMessage
from src.libraries.common.platform.lxns import SongIDConverter
from src.libraries.assets.get import assets, AssetType, JSONType
from src.libraries.common.images.text import (
    draw_truncated_text,
    draw_centered_text,
    draw_centered_truncated_text,
)
from src.libraries.common.game.maimai import rating_generator
from src.libraries.common.file.temp import TempFileManager
from config import FontPaths, BOT_NAME


class SongInfo:
    id: int
    title: str
    artist: str
    bpm: int
    genre: str
    map: str
    version: int
    song_type: str
    difficulties: Any


async def get_song_info(alias="", songid=0, debug=False):
    song_list = await assets.get_json(JSONType.LXNS_SONGS_INFO)

    if alias:
        logger.info(f"[SONGINFO] Searching for {alias}")
        # 请求 JSON 数据
        alias_data = await assets.get_json(JSONType.ALIAS)

        logger.info(f"[SONGINFO] Found {len(alias_data)} aliases")
        # 查找对应的歌曲 ID
        matching_songs_id_list = [
            int(song_id) for song_id, aliases in alias_data.items() if alias in aliases
        ]
        # 查找对应的歌曲 ID
        matching_songs_id_list = [
            int(song_id) for song_id, aliases in alias_data.items() if alias in aliases
        ]
        logger.info(f"[SONGINFO] Found {len(matching_songs_id_list)} matching songs")
        if not matching_songs_id_list:
            return []
    elif songid:
        matching_songs_id_list = [songid]
    else:
        return False

    # 保存匹配的曲目信息并分裂曲目
    split_songs_list: List[SongInfo] = []
    for song_id in matching_songs_id_list:
        for song in song_list["songs"]:

            if song["id"] == SongIDConverter.common_to_lxns_songid(song_id):

                song_info = SongInfo()

                song_info.id = song_id
                song_info.title = song["title"]
                song_info.artist = song["artist"]
                song_info.bpm = song["bpm"]
                song_info.genre = song["genre"]
                song_info.version = song["version"]
                song_info.map = ""

                if SongIDConverter.is_dx(song_id):
                    song_info.song_type = "DX"
                    song_info.difficulties = song["difficulties"]["dx"]
                    song_info.map = song.get("map", "")

                elif SongIDConverter.is_sd(song_id):
                    song_info.song_type = "SD"
                    song_info.difficulties = song["difficulties"]["standard"]

                else:
                    song_info.song_type = "utage"
                    song_info.difficulties = song["difficulties"]["utage"]

                split_songs_list.append(song_info)

    if len(split_songs_list) == 0:
        return False

    temp_file_manager = TempFileManager()
    image_List = []
    # 开始绘图
    for song_info in split_songs_list:
        print(f"Processing Song: {song_info.title}")
        # 加载背景图像
        bg = Image.open(await assets.get_async(AssetType.SONGINFO, "song_bg.png"))

        draw = ImageDraw.Draw(bg)

        # 准备封面与类别图像
        cover = Image.open(
            await assets.get_async(AssetType.COVER, song_info.id)
        ).resize((360, 360))

        cover_addr_map = {
            "maimai": "info-maimai.png",
            "POPSアニメ": "info-anime.png",
            "ゲームバラエティ": "info-game.png",
            "niconicoボーカロイド": "info-niconico.png",
            "オンゲキCHUNITHM": "info-ongeki.png",
            "東方Project": "info-touhou.png",
        }

        cover_addr_path = cover_addr_map.get(song_info.genre, "info-default.png")

        cover_addr = (
            Image.open(await assets.get_async(AssetType.SONGINFO, cover_addr_path))
            .convert("RGBA")
            .resize((400, 400))
        )

        # 将透明图片粘贴到背景上
        bg.paste(cover_addr, (202, 328), cover_addr)
        bg.paste(cover, (206, 336))

        # 绘制标题
        draw_truncated_text(
            draw,
            (633, 328),
            song_info.title,
            ImageFont.truetype(FontPaths.HANYI, 56),
            895,
            (0, 0, 0),
        )

        # 绘制艺术家
        draw_truncated_text(
            draw,
            (633, 428),
            song_info.artist,
            ImageFont.truetype(FontPaths.HANYI, 40),
            895,
            (0, 0, 0),
        )

        # 绘制分类和地图
        if song_info.map:
            text = f"{song_info.genre} / {song_info.map}"
        else:
            text = f"{song_info.genre}"
        draw_truncated_text(
            draw,
            (633, 575),
            text,
            ImageFont.truetype(FontPaths.HANYI, 40),
            900,
            (0, 0, 0),
        )

        # 版本映射字典
        version_map = {
            100: "maimai",
            110: "maimai PLUS",
            120: "maimai GreeN",
            130: "maimai GreeN PLUS",
            140: "maimai ORANGE",
            150: "maimai ORANGE PLUS",
            160: "maimai PiNK",
            170: "maimai PiNK PLUS",
            180: "maimai MURASAKi",
            185: "maimai MURASAKi PLUS",
            190: "maimai MiLK",
            195: "maimai MiLK PLUS",
            199: "maimai FiNALE",
            200: "wm_DX",
            210: "wm_DX2021",
            220: "wm_DX2022",
            230: "wm_DX2023",
            240: "wm_DX2024",
        }

        # 舞萌版本名称汉字映射字典
        version_name_map = {
            100: "真",
            110: "真",
            120: "超",
            130: "檄",
            140: "橙",
            150: "晓",
            160: "桃",
            170: "樱",
            180: "紫",
            185: "堇",
            190: "白",
            195: "雪",
            199: "辉",
            200: "熊/華",
            210: "爽/煌",
            220: "宙/星",
            230: "祭/祝",
            240: "双/?",
        }

        # 获取歌曲版本
        version_key = int(song_info.difficulties[0]["version"] / 100)
        version_name = version_map.get(version_key, "maimai")
        version_name_chinese = version_name_map.get(version_key, "")

        # 加载对应版本的图片
        version_image = Image.open(
            await assets.get_async(AssetType.SONGINFO, f"{version_name}.png")
        ).convert("RGBA")

        # 绘制BPM
        color = (0, 0, 0)
        if song_info.bpm > 250:
            color = (255, 12, 0)
        draw.text(
            (700, 494),
            f"{song_info.bpm}",
            font=ImageFont.truetype(FontPaths.TORUS_BOLD, 45),
            fill=color,
        )

        # 绘制版本汉字
        draw.text(
            (850, 505),
            f"牌子: {version_name_chinese}",
            font=ImageFont.truetype(FontPaths.HANYI, 35),
            fill=(0, 0, 0),
        )

        # 计算新的高度，保持原比例
        height = 200
        original_width, original_height = version_image.size
        width = int((height / original_height) * original_width)

        # 缩放图片
        version_image = version_image.resize((width, height))

        # 在背景图上粘贴版本图片
        bg.paste(version_image, (100, 45), version_image)

        # 绘制类型
        if song_info.song_type != "utage":
            type_badge = Image.open(
                await assets.get_async(AssetType.SONGINFO, f"{song_info.song_type}.png")
            ).convert("RGBA")
            bg.paste(type_badge, (420, 640), type_badge)

        # 绘制难度
        print("Processing Levels...", song_info.difficulties)
        for level_index, difficulty in enumerate(song_info.difficulties):
            # 打开并处理背景图像
            level_bg = (
                Image.open(
                    await assets.get_async(AssetType.SONGINFO, f"d-{level_index}.png")
                )
                .convert("RGBA")
                .resize((120, 48))
            )

            # 创建一个绘制对象
            level_bg_draw = ImageDraw.Draw(level_bg)

            # 获取文字内容
            draw_centered_text(
                level_bg_draw,
                (60, 2),
                difficulty["level"],
                ImageFont.truetype(FontPaths.HANYI, 40),
                (255, 255, 255),
            )
            # 将处理后的图像粘贴到背景图上
            bg.paste(level_bg, (633 + level_index * 140, 650), level_bg)

            column_x = 445
            column_y = 930

            # 绘制铺面难度
            draw_centered_text(
                draw,
                (column_x - 168, column_y + level_index * 110 + 28),
                difficulty["level"],
                ImageFont.truetype(FontPaths.HANYI, 36),
                (255, 255, 255),
            )

            draw_centered_text(
                draw,
                (column_x + 30, column_y + level_index * 110 - 10),
                f"{difficulty['level_value']}",
                ImageFont.truetype(FontPaths.TORUS_BOLD, 60),
                (0, 0, 0),
            )

            if level_index > 1:
                draw_centered_truncated_text(
                    draw,
                    (column_x + 90, column_y + level_index * 75 + 500),
                    f"{difficulty['note_designer']}",
                    ImageFont.truetype(FontPaths.SIYUAN, 35),
                    300,
                    (0, 0, 0),
                )
                for j, (grade, rating) in enumerate(
                    rating_generator(difficulty["level_value"])
                ):
                    color = (0, 0, 0)
                    if rating > 280:
                        color = (218, 165, 32)
                    if rating > 290:
                        color = (255, 165, 0)
                    if rating > 300:
                        color = (220, 20, 60)
                    if rating > 310:
                        color = (255, 0, 0)
                    if rating > 320:
                        color = (148, 0, 211)
                    draw_centered_text(
                        draw,
                        (column_x + 324 + j * 155, column_y + level_index * 75 + 500),
                        f"{rating}",
                        ImageFont.truetype(FontPaths.TORUS_BOLD, 40),
                        color,
                    )

            # 绘制铺面notes
            for index, (key, value) in enumerate(difficulty["notes"].items()):
                x = column_x + 40 + (index + 1) * 175
                y = column_y + level_index * 110
                draw_centered_text(
                    draw,
                    (x, y),
                    f"{value}",
                    ImageFont.truetype(FontPaths.TORUS_BOLD, 50),
                    (0, 0, 0),
                )

            # 绘制Footer
            draw.text(
                (630, 1880),
                f"Generated by {BOT_NAME}",
                font=ImageFont.truetype(FontPaths.HANYI, 35),
                fill=(0, 0, 0),
            )

        path, name = temp_file_manager.create_temp_image_file(bg)
        image_List.append(path)
        if debug:
            bg.show()
            print(path)
    return image_List


async def search_by_args(args: str, mix_message: MixMessage):
    if not args:
        await mix_message.reply(
            content=(
                "请输入歌曲别名或ID\n" "例如：/查歌 xxx\n" "你也可以直接问xxx是什么歌\n"
            )
        )
    try:
        if args.isdigit():
            song_id = int(args)
            image_url_list = await get_song_info(songid=song_id)
            if image_url_list and len(image_url_list) > 0:
                await mix_message.reply(file_image=image_url_list[0])
            else:
                await mix_message.reply(content=f"😢没有找到ID=[{song_id}]的乐曲]")

        else:
            alias = args
            image_url_list = await get_song_info(alias=alias)
            if image_url_list and len(image_url_list) > 0:
                for image_url in image_url_list:
                    await mix_message.reply(file_image=image_url)
            else:
                await mix_message.reply(content=f"😢没有找到被称作为[{alias}]的乐曲]")

    except Exception as e:
        logger.error(f"[SONGINFO] Get Error {e}")
        await mix_message.reply(content="获取歌曲数据出错啦")


async def get_song_by_alias(message: GroupMessage | Message):
    mix_message = MixMessage(message)
    args = mix_message.get_args("查歌")
    await search_by_args(args, mix_message)


async def handle_what_song(message: GroupMessage | Message):
    mix_message = MixMessage(message)
    if "是什么歌" in mix_message.content:
        args = mix_message.get_args("是什么歌", 0)
        if args:
            logger.info(f"[SONGINFO] {args} 是什么歌")
            await search_by_args(args, mix_message)
    return False


# 定义支持的指令及其处理函数（指令名应为小写）
COMMANDS = {
    "查歌": get_song_by_alias,
}

DEFAULT_HANDLER = handle_what_song


# 默认大写的插件名
COMMAND_NAME = "SONG_INFO"

# 指令范围
COMMAND_SCOPE = "both"
