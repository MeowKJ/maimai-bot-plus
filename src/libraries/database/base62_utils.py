# my_database_lib/base62_utils.py

import string

# 设置日志配置
from botpy import logger

BASE62_ALPHABET = string.ascii_letters + string.digits
BASE62_ALPHABET_MAP = {char: index for index, char in enumerate(BASE62_ALPHABET)}
BASE62_BASE = len(BASE62_ALPHABET)


def encode_base62(number: int) -> str:
    if number == 0:
        return BASE62_ALPHABET[0]

    base62_string = []
    while number:
        number, remainder = divmod(number, BASE62_BASE)
        base62_string.append(BASE62_ALPHABET[remainder])

    encoded = "".join(reversed(base62_string))
    logger.info(f"[Database] Encoded number {number} to Base62 string {encoded}.")
    return encoded


def decode_base62(base62_string: str) -> int:
    number = 0
    for char in base62_string:
        number = number * BASE62_BASE + BASE62_ALPHABET_MAP[char]
    logger.info(f"[Database] Decoded Base62 string {base62_string} to number {number}.")
    return number
