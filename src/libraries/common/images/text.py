from PIL import ImageDraw, ImageFont
from typing import Tuple


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    position: Tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: Tuple[int, int, int] = (0, 0, 0),
) -> None:
    """
    绘制水平居中的文本。

    Args:
        draw (ImageDraw.ImageDraw): 用于绘制的 ImageDraw 对象。
        center_x (int): 文本水平居中的 x 坐标。
        y (int): 文本的 y 坐标。
        text (str): 需要绘制的文本内容。
        font (ImageFont.ImageFont): 绘制文本所使用的字体对象。
        fill (Tuple[int, int, int]): 文本颜色，格式为 RGB 元组。

    Returns:
        None: 该函数没有返回值。
    """
    # 使用 getbbox 获取文本的边界框
    bbox = font.getbbox(text)
    text_width = bbox[2] - bbox[0]  # bbox[2] 是右边界，bbox[0] 是左边界

    # 计算居中后的 x 位置
    x = position[0] - text_width // 2

    # 绘制文本
    draw.text((x, position[1]), text, font=font, fill=fill)


def draw_truncated_text(
    draw: ImageDraw.ImageDraw,
    position: Tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    max_width: int,
    fill: Tuple[int, int, int],
) -> None:
    """
    绘制带省略号的文本，当文本超出指定宽度时自动截断。

    Args:
        draw (ImageDraw.ImageDraw): 用于绘制的 ImageDraw 对象。
        position (Tuple[int, int]): 文本的绘制位置 (x, y)。
        text (str): 需要绘制的文本内容。
        font (ImageFont.ImageFont): 绘制文本所使用的字体对象。
        max_width (int): 文本允许的最大宽度，超出此宽度将被截断并添加省略号。
        fill (Tuple[int, int, int]): 文本颜色，格式为 RGB 元组。

    Returns:
        None: 该函数没有返回值。
    """
    # 测量文本宽度
    text_width = draw.textlength(text, font=font)

    # 如果文本宽度超过最大宽度
    if text_width > max_width:
        # 逐步截取文本并添加省略号，直到宽度合适
        ellipsis = "..."
        ellipsis_width = draw.textlength(ellipsis, font=font)

        # 确保截取后的文本加上省略号不会超出最大宽度
        while text_width + ellipsis_width > max_width and len(text) > 0:
            text = text[:-1]  # 移除最后一个字符
            text_width = draw.textlength(text, font=font)

        # 加上省略号
        text += ellipsis

    # 绘制文本
    draw.text(position, text, font=font, fill=fill)


def draw_centered_truncated_text(
    draw: ImageDraw.ImageDraw,
    position: Tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    max_width: int,
    fill: Tuple[int, int, int] = (0, 0, 0),
) -> None:
    """
    绘制水平居中的文本，当文本超出指定宽度时自动截断并添加省略号。

    Args:
        draw (ImageDraw.ImageDraw): 用于绘制的 ImageDraw 对象。
        position (Tuple[int, int]): 文本的绘制位置 (center_x, y)。
        text (str): 需要绘制的文本内容。
        font (ImageFont.ImageFont): 绘制文本所使用的字体对象。
        max_width (int): 文本允许的最大宽度，超出此宽度将被截断并添加省略号。
        fill (Tuple[int, int, int]): 文本颜色，格式为 RGB 元组。

    Returns:
        None: 该函数没有返回值。
    """
    # 测量文本宽度
    text_width = draw.textlength(text, font=font)

    # 如果文本宽度超过最大宽度
    if text_width > max_width:
        # 逐步截取文本并添加省略号，直到宽度合适
        ellipsis = "..."
        ellipsis_width = draw.textlength(ellipsis, font=font)

        # 确保截取后的文本加上省略号不会超出最大宽度
        while text_width + ellipsis_width > max_width and len(text) > 0:
            text = text[:-1]  # 移除最后一个字符
            text_width = draw.textlength(text, font=font)

        # 加上省略号
        text += ellipsis

    # 重新计算截断后文本的宽度
    text_width = draw.textlength(text, font=font)

    # 计算居中后的 x 位置
    x = position[0] - text_width // 2

    # 绘制文本
    draw.text((x, position[1]), text, font=font, fill=fill)
