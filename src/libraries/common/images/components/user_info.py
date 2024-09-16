from typing import List, Dict, Any, Union, TYPE_CHECKING
import random
from io import BytesIO
import aiohttp

from src.libraries.common.game.maimai import UserInfo
from src.libraries.assets import assets, AssetType
from PIL import Image, ImageDraw, ImageFont
from ..alpha import add_rounded_corners_to_image, adjust_image_alpha
from ..text import draw_truncated_text, draw_centered_text

from config import FontPaths


async def _get_avatar_image(avatar: str, default_avatar: str) -> Image.Image:
    if avatar.isdigit():
        return Image.open(await assets.get_async(AssetType.AVATAR, avatar))
    elif avatar.startswith("http"):
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar) as resp:
                return Image.open(BytesIO(await resp.read()))

    return Image.open(default_avatar)


def _get_rating_image_name(rating: int) -> str:
    thresholds = [1000, 2000, 4000, 7000, 10000, 12000, 13000, 14000, 14500, 15000]
    num = next(
        (f"{i+1:02d}" for i, threshold in enumerate(thresholds) if rating < threshold),
        "11",
    )
    return f"UI_CMN_DXRating_{num}.png"


async def draw_user_info(
    userinfo: UserInfo,
    addictional_text: str,
    default_name_plate: str,
    default_avatar: str,
) -> Image.Image:

    # 获取姓名框 nameplate
    if userinfo.nameplate_id:
        name_plate_path = await assets.get_async(AssetType.PLATE, userinfo.nameplate_id)
    elif default_name_plate:
        name_plate_path = default_name_plate
    else:
        raise ValueError("No nameplate provided. 没有提供姓名框。")

    # 使用姓名框作为主要图
    main_image = Image.open(name_plate_path).resize((1420, 230)).convert("RGBA")
    main_image = add_rounded_corners_to_image(main_image, 20)

    # 1.制作头像和头像框
    # 数据
    avatar_base_offset = (8, 8)
    avatar_size = (206, 206)
    avatar_border_size = (214, 214)
    avatar_offset = (4, 4)
    # 获取头像
    avatar_img = await _get_avatar_image(userinfo.avatar, default_avatar)
    avatar_img = avatar_img.convert("RGBA").resize(avatar_size)
    avatar_img = add_rounded_corners_to_image(avatar_img, 15)
    avatar_border_img = (
        Image.open(assets.get(AssetType.PRISM, "avatar_border.png"))
        .resize(avatar_border_size)
        .convert("RGBA")
    )
    avatar_border_img.alpha_composite(avatar_img, avatar_offset)
    main_image.alpha_composite(avatar_border_img, avatar_base_offset)

    # 2.绘制rating
    # 数据
    dx_rating_base_offset = (230, 22)

    dx_rating_image = (
        Image.open(
            assets.get(AssetType.IMAGES, _get_rating_image_name(userinfo.rating))
        )
        .resize((300, 59))
        .convert("RGBA")
    )

    rating = f"{userinfo.rating:05d}"
    for n, i in enumerate(rating):
        dx_rating_image.alpha_composite(
            Image.open(
                await assets.get_async(AssetType.IMAGES, f"UI_NUM_Drating_{i}.png")
            )
            .resize((28, 34))
            .convert("RGBA"),
            (140 + 23 * n, 15),
        )

    main_image.alpha_composite(dx_rating_image, dx_rating_base_offset)

    # 3.绘制友人对战阶级(class_rank)
    class_rank_base_offset = (1035, 110)
    if userinfo.class_rank:
        class_level_img = (
            Image.open(
                await assets.get_async(AssetType.CLASS_RANK, userinfo.class_rank)
            )
            .resize((144, 87))
            .convert("RGBA")
        )
        main_image.alpha_composite(class_level_img, class_rank_base_offset)

    # 4.绘制姓名框和段位(course_rank), 做透明处理
    name_base_offset = (230, 100)

    name_image = Image.open(
        await assets.get_async(AssetType.IMAGES, "Name.png")
    ).convert("RGBA")

    name_image = adjust_image_alpha(name_image, 0.6)

    # 绘制姓名
    name_draw = ImageDraw.Draw(name_image)
    if userinfo.course_rank:
        max_width = 310
        class_level_img = (
            Image.open(
                await assets.get_async(AssetType.COURSE_RANK, userinfo.course_rank)
            )
            .resize((134, 55))
            .convert("RGBA")
        )
        name_image.alpha_composite(class_level_img, (315, 8))

    else:
        max_width = 430

    draw_truncated_text(
        name_draw,
        (12, 3),
        userinfo.username,
        ImageFont.truetype(FontPaths.SIYUAN, 40),
        max_width,
        (0, 0, 0, 255),
    )
    main_image.alpha_composite(name_image, name_base_offset)

    # 5.绘制彩虹条
    rainbow_base_offset = (234, 175)
    rainbow_image = (
        Image.open(
            await assets.get_async(AssetType.IMAGES, "UI_CMN_Shougou_Rainbow.png")
        )
        .resize((454, 50))
        .convert("RGBA")
    )
    rainbow_draw = ImageDraw.Draw(rainbow_image)
    rainbow_draw.text(
        (227, 21),
        addictional_text,
        (0, 0, 0, 255),
        ImageFont.truetype(FontPaths.SIYUAN, 28),
        anchor="mm",
        stroke_fill=(255, 255, 255, 255),
        stroke_width=3,
    )

    main_image.alpha_composite(rainbow_image, rainbow_base_offset)

    return main_image
