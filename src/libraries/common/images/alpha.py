from PIL import Image, ImageDraw, ImageOps, ImageEnhance
from typing import Any


def adjust_image_alpha(image: Image.Image, alpha: float) -> Image.Image:
    """
    Adjusts the alpha (transparency) of an image while preserving the fully transparent areas.

    Args:
        image (Image.Image): The image object to adjust.
        alpha (float): The new alpha level to apply to non-transparent areas (0.0 to 1.0).

    Returns:
        Image.Image: The adjusted image with modified alpha levels.

    Raises:
        ValueError: If `alpha` is not in the range of 0.0 to 1.0.
    """
    # 检查alpha值是否在0.0到1.0之间
    if not (0.0 <= alpha <= 1.0):
        raise ValueError("Alpha must be between 0.0 and 1.0")

    # 确保图像是 RGBA 模式
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # 分离图像的 RGBA 通道
    r, g, b, alpha_channel = image.split()

    # 创建一个新的 alpha 通道，其中原透明部分保持不变，非透明部分应用新的透明度
    new_alpha = alpha_channel.point(lambda i: int(i * alpha) if i > 0 else 0)

    # 将新的 alpha 通道与原来的 RGB 通道合并
    adjusted_image = Image.merge("RGBA", (r, g, b, new_alpha))

    return adjusted_image


def add_rounded_corners_to_image(image: Image.Image, radius: int) -> Image.Image:
    """
    Adds rounded corners to the given image.

    This function takes an image as input and applies rounded corners with the specified
    radius. The resulting image will have transparent corners (if the input image has no alpha
    channel, one will be added).

    Args:
        image (Image.Image): The input image in which to add rounded corners.
        radius (int): The radius of the rounded corners. Higher values result in more
                      pronounced rounded corners.

    Returns:
        Image.Image: The resulting image with rounded corners.

    Raises:
        ValueError: If the radius is negative or if the input image is not a valid instance of Image.

    Example:
        >>> original_image = Image.open("example.jpg")
        >>> rounded_image = add_rounded_corners_to_image(original_image, 30)
        >>> rounded_image.show()
    """
    if not isinstance(image, Image.Image):
        raise ValueError("The input must be a valid PIL Image.")

    if radius < 0:
        raise ValueError("The radius must be non-negative.")

    # Ensure the image has an alpha channel for transparency
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # Create a mask for the rounded corners
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)

    # Draw a rounded rectangle on the mask
    left_up_point = (0, 0)
    right_down_point = image.size
    draw.rounded_rectangle([left_up_point, right_down_point], radius=radius, fill=255)

    # Apply the mask to the original image
    rounded_image = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
    rounded_image.putalpha(mask)

    return rounded_image


def deepen_image_color(image: Image.Image, factor: float) -> Image.Image:
    """
    Deepens the color of the given image by increasing its color saturation.

    Args:
        image (Image.Image): The input image whose color saturation will be increased.
        factor (float): A multiplier to adjust the color saturation. Values greater than 1.0 
                        will deepen the colors. Values less than 1.0 will desaturate the image.

    Returns:
        Image.Image: The resulting image with deeper colors.
    
    Raises:
        ValueError: If the factor is negative or the input image is not a valid instance of Image.
    
    Example:
        >>> original_image = Image.open("example.jpg")
        >>> deepened_image = deepen_image_color(original_image, 1.5)
        >>> deepened_image.show()
    """
    if not isinstance(image, Image.Image):
        raise ValueError("The input must be a valid PIL Image.")
    
    if factor < 0:
        raise ValueError("The factor must be non-negative.")
    
    # Enhance the color of the image
    enhancer = ImageEnhance.Color(image)
    deepened_image = enhancer.enhance(factor)
    
    return deepened_image
