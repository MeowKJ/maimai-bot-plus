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
