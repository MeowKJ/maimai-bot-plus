import asyncio
import os
import subprocess
import re


def is_fish_else_lxns(args: str) -> bool:
    """
    检查输入是否是一个有效的 QQ 号。
    QQ 号是一个 5 到 11 位的数字。

    参数:
    - args (str): 要检查的字符串。

    返回:
    - bool
    """
    # 正则表达式用于匹配 5 到 11 位的数字
    pattern = r"^\d{5,11}$"

    # 使用正则表达式进行匹配
    if re.match(pattern, args):
        return False
    else:
        return True


async def compress_png(fp, output, force=True, quality=None):
    """
    Compresses a PNG file asynchronously.

    Args:
        fp (str): The file path of the original PNG file.
        output (str): The file path for the compressed PNG file.
        force (bool, optional): Whether to force compression. Defaults to True.
        quality (int or str, optional): Compression quality parameter. Defaults to None.

    Returns:
        float: Compression ratio percentage.
    """
    if not os.path.exists(fp):
        raise FileNotFoundError(f"File not found: {fp}")

    force_command = "-f" if force else ""
    quality_command = ""

    if quality and isinstance(quality, int):
        quality_command = f"--quality {quality}"
    if quality and isinstance(quality, str):
        quality_command = f"--quality {quality}"

    command = (
        f"pngquant {fp} "
        f"--skip-if-larger {force_command} "
        f"{quality_command} "
        f"--output {output}"
    )

    try:
        process = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        # 获取原始图像大小
        original_size = os.path.getsize(fp)

        # 获取压缩后文件的大小
        compressed_size = os.path.getsize(output)

        # 计算压缩比
        compression_ratio = (1 - compressed_size / original_size) * 100

        # 检查命令是否成功执行
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command)

        return compression_ratio
    except asyncio.CancelledError as exc:
        raise exc from None
    except Exception as e:
        raise RuntimeError(f"An error occurred: {e}") from e
