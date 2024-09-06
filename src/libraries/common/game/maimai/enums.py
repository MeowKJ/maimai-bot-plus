from typing import Any, Dict, List, Optional, Tuple, Union
from enum import Enum

# 枚举：Maimai 用户平台类型
class MaimaiUserPlatform(Enum):
    """Maimai 用户平台枚举类。

    Attributes:
        DIVING_FISH (int): 水鱼查分器，对应枚举值 0。
        LXNS (int): 落雪咖啡屋查分器，对应枚举值 1。
    """
    DIVING_FISH = 0  # 水鱼查分器
    LXNS = 1  # 落雪咖啡屋查分器


# 枚举：歌曲类型
class SongType(Enum):
    """歌曲类型枚举类。

    Attributes:
        STANDARD (int): 标准铺面，对应枚举值 0。
        DX (int): DX 铺面，对应枚举值 1。
        UTAGE (int): 宴会场铺面，对应枚举值 2。
    """
    STANDARD = 0  # 标准铺面
    DX = 1  # DX 铺面
    UTAGE = 2  # 宴会场铺面


# 枚举：铺面难度对应的字符
class SongLevelText(Enum):
    """铺面难度对应的字符枚举类。

    Attributes:
        BASIC (str): 基础难度 "BASIC"。
        ADVANCED (str): 高级难度 "ADVANCED"。
        EXPERT (str): 专家难度 "EXPERT"。
        MASTER (str): 大师难度 "MASTER"。
        RE_MASTER (str): 超大师难度 "RE:MASTER"。
    """
    BASIC = "BASIC"  # 基础难度
    ADVANCED = "ADVANCED"  # 高级难度
    EXPERT = "EXPERT"  # 专家难度
    MASTER = "MASTER"  # 大师难度
    RE_MASTER = "RE:MASTER"  # 超大师难度


# 枚举：铺面难度
class SongLevel(Enum):
    """铺面难度枚举类。

    Attributes:
        BASIC (int): 基础难度，对应枚举值 0。
        ADVANCED (int): 高级难度，对应枚举值 1。
        EXPERT (int): 专家难度，对应枚举值 2。
        MASTER (int): 大师难度，对应枚举值 3。
        RE_MASTER (int): 超大师难度，对应枚举值 4。
    """
    BASIC = 0  # 基础难度
    ADVANCED = 1  # 高级难度
    EXPERT = 2  # 专家难度
    MASTER = 3  # 大师难度
    RE_MASTER = 4  # 超大师难度


# 铺面难度与其对应字符的映射字典
SongLevelTextMap = {
    SongLevel.BASIC: SongLevelText.BASIC,  # 基础难度映射到字符 "BASIC"
    SongLevel.ADVANCED: SongLevelText.ADVANCED,  # 高级难度映射到字符 "ADVANCED"
    SongLevel.EXPERT: SongLevelText.EXPERT,  # 专家难度映射到字符 "EXPERT"
    SongLevel.MASTER: SongLevelText.MASTER,  # 大师难度映射到字符 "MASTER"
    SongLevel.RE_MASTER: SongLevelText.RE_MASTER  # 超大师难度映射到字符 "RE:MASTER"
}
