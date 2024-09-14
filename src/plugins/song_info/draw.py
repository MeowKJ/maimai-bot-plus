from typing import List
from PIL import Image, ImageDraw, ImageFont

from botpy import logger

from src.libraries.assets import assets, AssetType, JSONType
from src.libraries.common.images import (
    draw_truncated_text,
    draw_centered_text,
    draw_centered_truncated_text,
    resize_image,
)

from src.libraries.common.game.maimai import Song, SongType, UserInfo
from src.libraries.common.game.maimai.maimai import MaimaiHelper

from config import FontPaths, BOT_NAME, DEBUG, VERSION


COVER_ADDR_MAP = {
    "maimai": "info-maimai.png",
    "POPSアニメ": "info-anime.png",
    "ゲームバラエティ": "info-game.png",
    "niconicoボーカロイド": "info-niconico.png",
    "オンゲキCHUNITHM": "info-ongeki.png",
    "東方Project": "info-touhou.png",
}

VERSION_IMAGE_MAP = {
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
VERSION_NAME_MAP = {
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


async def get_song_info_id_list_from_alias(alias: str) -> List[int]:
    alias = alias.lower().replace(" ", "")
    alias_data = await assets.get_json(JSONType.ALIAS)
    return [
        int(song_id)
        for song_id, aliases in alias_data.items()
        if alias in [a.lower().replace(" ", "") for a in aliases]
    ]


async def create_selected_song_image(song_data_list: List[Song]) -> Image.Image:
    font_id = ImageFont.truetype(FontPaths.TORUS_BOLD, 40)
    font_title = ImageFont.truetype(FontPaths.HANYI, 25)
    image_height_per_entry = 120

    total_height = image_height_per_entry * len(song_data_list)

    result_image = Image.new("RGB", (500, total_height), color=(255, 255, 255))

    for index, song in enumerate(song_data_list):

        cover_url = await assets.get_async(AssetType.COVER, song.id)
        cover_image = Image.open(cover_url).resize((100, 100)).convert("RGBA")

        type_badge_target_height = 20

        type_badge = Image.open(
            await assets.get_async(AssetType.SONGINFO, f"{song.song_type.value}.png")
        ).convert("RGBA")

        type_badge_width, type_badge_height = type_badge.size
        type_badge_target_width = int(
            (type_badge_target_height / type_badge_height) * type_badge_width
        )
        type_badge = type_badge.resize(
            (type_badge_target_width, type_badge_target_height)
        )

        cover_image.paste(type_badge, (2, 2), type_badge)

        y_offset = 10 + index * image_height_per_entry
        result_image.paste(cover_image, (10, y_offset))
        draw = ImageDraw.Draw(result_image)
        draw_truncated_text(
            draw,
            (120, y_offset + 10),
            f"ID:{song.id}",
            font=font_id,
            fill=(0, 0, 0),
            max_width=350,
        )
        draw_truncated_text(
            draw,
            (120, y_offset + 60),
            song.title,
            font=font_title,
            fill=(0, 0, 0),
            max_width=350,
        )

    if DEBUG:
        result_image.show()

    return result_image


async def create_song_info_image(song: Song) -> Image.Image:
    logger.info(f"[SONGINFO] Creating image for {song.id}...")

    # 加载背景图像
    bg = Image.open(
        await assets.get_async(AssetType.SONGINFO, "songinfo_bg.png")
    ).convert("RGBA")

    draw = ImageDraw.Draw(bg)

    # 准备封面与类别图像
    cover = Image.open(await assets.get_async(AssetType.COVER, song.id)).resize(
        (360, 360)
    )

    cover_addr_path = COVER_ADDR_MAP.get(song.genre, "info-default.png")

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
        song.title,
        ImageFont.truetype(FontPaths.HANYI, 56),
        895,
        (0, 0, 0),
    )

    # 绘制艺术家
    draw_truncated_text(
        draw,
        (633, 428),
        song.artist,
        ImageFont.truetype(FontPaths.HANYI, 40),
        895,
        (0, 0, 0),
    )

    # 绘制分类和地图
    if song._map:
        text = f"{song.genre} / {song._map}"
    else:
        text = f"{song.genre}"
    draw_truncated_text(
        draw,
        (633, 575),
        text,
        ImageFont.truetype(FontPaths.HANYI, 40),
        900,
        (0, 0, 0),
    )
    # 获取歌曲版本
    version_key = int(song.version / 100)
    version_image_name = VERSION_IMAGE_MAP.get(version_key, "maimai")
    version_name_chinese = VERSION_NAME_MAP.get(version_key, "")

    # 加载对应版本的图片
    version_image = Image.open(
        await assets.get_async(AssetType.SONGINFO, f"{version_image_name}.png")
    ).convert("RGBA")

    # 绘制BPM
    color = (0, 0, 0)
    if song.bpm > 250:
        color = (255, 12, 0)
    draw.text(
        (700, 494),
        f"{song.bpm}",
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
    if song.song_type != SongType.UTAGE:
        type_badge = Image.open(
            await assets.get_async(AssetType.SONGINFO, f"{song.song_type.value}.png")
        ).convert("RGBA")
        bg.paste(type_badge, (420, 640), type_badge)

    # 绘制难度
    for level_index, difficulty in enumerate(song.difficulties):
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
            difficulty.level_lable,
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
            difficulty.level_lable,
            ImageFont.truetype(FontPaths.HANYI, 36),
            (255, 255, 255),
        )

        draw_centered_text(
            draw,
            (column_x + 30, column_y + level_index * 110 - 10),
            f"{difficulty.level}",
            ImageFont.truetype(FontPaths.TORUS_BOLD, 60),
            (0, 0, 0),
        )

        if level_index > 1:
            draw_centered_truncated_text(
                draw,
                (column_x + 90, column_y + level_index * 75 + 500),
                difficulty.note_designer,
                ImageFont.truetype(FontPaths.SIYUAN, 35),
                300,
                (0, 0, 0),
            )
            for j, (grade, rating) in enumerate(
                MaimaiHelper.rating_generator(difficulty.level)
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
        for index, (key, value) in enumerate(difficulty.notes.to_dict().items()):
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
            (525, 1880),
            f"Generated by {BOT_NAME}",
            font=ImageFont.truetype(FontPaths.HANYI, 35),
            fill=(0, 0, 0),
        )

        # 绘制Version
        draw.text(
            (1150, 1880),
            f"({VERSION})",
            font=ImageFont.truetype(FontPaths.TORUS_BOLD, 30),
            fill=(0, 0, 0),
        )
    return bg


async def create_song_score_image(
    song: Song, user_info: UserInfo = None
) -> Image.Image:

    font_color_basic = (18, 55, 139)

    bg = await assets.get_async(AssetType.IMAGES, "info_bg.png")
    cover = await assets.get_async(AssetType.COVER, song.id)

    bg_img = Image.open(bg)

    cover_img = Image.open(cover).resize((450, 450)).convert("RGBA")
    cover_addr_path = COVER_ADDR_MAP.get(song.genre, "info-default.png")
    cover_addr = (
        Image.open(await assets.get_async(AssetType.SONGINFO, cover_addr_path))
        .resize((500, 500))
        .convert("RGBA")
    )

    cover_addr.paste(cover_img, (5, 10), cover_img)

    bg_img.paste(cover_addr, (150, 400), cover_addr)

    draw = ImageDraw.Draw(bg_img)

    # 绘制标题
    draw_centered_truncated_text(
        draw,
        (390, 900),
        song.title,
        ImageFont.truetype(FontPaths.HANYI, 50),
        600,
        font_color_basic,
    )

    # 绘制ID
    draw_centered_text(
        draw,
        (240, 1030),
        f"{song.id}",
        ImageFont.truetype(FontPaths.TORUS_BOLD, 40),
        font_color_basic,
    )

    # 绘制BPM
    draw_centered_text(
        draw,
        (490, 1030),
        f"{song.bpm}",
        ImageFont.truetype(FontPaths.TORUS_BOLD, 40),
        font_color_basic,
    )

    for index, difficulty in enumerate(song.difficulties):
        level_bg_img = (
            Image.open(await assets.get_async(AssetType.SONGINFO, f"d-{index}.png"))
            .convert("RGBA")
            .resize((120, 48))
        )
        level_bg_img_draw = ImageDraw.Draw(level_bg_img)
        # 保留一位小数
        draw_centered_text(
            level_bg_img_draw,
            (60, 2),
            f"{difficulty.level:.1f}",
            ImageFont.truetype(FontPaths.HANYI, 40),
            (255, 255, 255),
        )
        # 如果有user_score则绘制
        if difficulty.user_score:
            # 绘制Achievement
            draw.text(
                (750, 415 + index * 150),
                f"{difficulty.user_score.achievements:.4f}%",
                font=ImageFont.truetype(FontPaths.TORUS_BOLD, 50),
                fill=font_color_basic,
            )

            # 绘制rate

            rate_img = Image.open(
                await assets.get_async(
                    AssetType.RANK, f"{difficulty.user_score.rate.value}"
                )
            ).convert("RGBA")
            rate_img = resize_image(rate_img, height=70)
            bg_img.paste(rate_img, (1030, 410 + index * 150), rate_img)

            # 绘制fsfc
            fcfs_img = Image.open(
                await assets.get_async(AssetType.IMAGES, "fcfs.png")
            ).convert("RGBA")
            fcfs_img = resize_image(fcfs_img, height=110)

            if difficulty.user_score.fc.value:
                fc_img = Image.open(
                    await assets.get_async(
                        AssetType.BADGE, f"{difficulty.user_score.fc.value}"
                    )
                ).convert("RGBA")
                fc_img = resize_image(fc_img, height=80)
                fcfs_img.paste(fc_img, (13, 13), fc_img)

            if difficulty.user_score.fs.value:
                fs_img = Image.open(
                    await assets.get_async(
                        AssetType.BADGE, f"{difficulty.user_score.fs.value}"
                    )
                ).convert("RGBA")
                fs_img = resize_image(fs_img, height=80)
                fcfs_img.paste(fs_img, (91, 13), fs_img)

            bg_img.paste(fcfs_img, (1220, 385 + index * 150), fcfs_img)

        bg_img.paste(level_bg_img, (1000, 350 + index * 150), level_bg_img)
    draw.text(
        (550, 1245),
        f"Generated by {BOT_NAME} [{VERSION}]",
        font=ImageFont.truetype(FontPaths.HANYI, 30),
        fill=font_color_basic,
    )
    return bg_img
