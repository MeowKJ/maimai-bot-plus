from PIL.Image import Image


# 相对调整大小，只需要制定宽度或者是高度
def resize_image(image: Image, width=None, height=None) -> Image:
    """
    调整图片大小。

    Args:
        image (PIL.Image.Image): 需要调整大小的图片对象。
        width (int): 调整后的宽度。
        height (int): 调整后的高度。

    Returns:
        PIL.Image.Image: 调整大小后的图片对象。
    """
    # 获取原始图片的宽高
    original_width, original_height = image.size

    # 计算调整后的宽高
    if width is None:
        width = int(original_width * height / original_height)
    if height is None:
        height = int(original_height * width / original_width)

    # 调整图片大小
    return image.resize((width, height))
