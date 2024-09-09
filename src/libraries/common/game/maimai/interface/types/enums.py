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

    STANDARD = "standard"  # 标准铺面
    DX = "dx"  # DX 铺面
    UTAGE = "utage"  # 宴会场铺面


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
    RE_MASTER = "Re:MASTER"  # 超大师难度


"""
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
"""


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
SongLevelTextMap = [
    SongLevelText.BASIC,  # 基础难度映射到字符 "BASIC"
    SongLevelText.ADVANCED,  # 高级难度映射到字符 "ADVANCED"
    SongLevelText.EXPERT,  # 专家难度映射到字符 "EXPERT"
    SongLevelText.MASTER,  # 大师难度映射到字符 "MASTER"
    SongLevelText.RE_MASTER,  # 超大师难度映射到字符 "RE:MASTER"
]


class SongRateType(Enum):
    """铺面评级枚举类。

    Attributes:
        SSS (str): SSS 级评级 "SSS"。
        SS (str): SS 级评级 "SS"。
        S (str): S 级评级 "S"。
    """

    SSS_PLUS = "sssp"  # SSS 级评级
    SSS = "sss"  # SSS 级评级
    SS_PLUS = "ssp"  # SS 级评级
    SS = "ss"  # SS 级评级
    S_PLUS = "sp"  # S 级评级
    S = "s"  # S 级评级
    AAA = "aaa"  # AAA 级评级
    AA = "aa"  # AA 级评级
    A = "a"  # A 级评级
    BBB = "bbb"  # B 级评级
    BB = "bb"  # BB 级评级
    B = "b"  # B 级评级
    C = "c"  # C 级评级
    D = "d"  # D 级评级


class FSType(Enum):
    """FS 类型枚举类。

    Attributes:
        FULL_SNYC (str): FULL COMBO 类型 "fs"。
        FULL_SNYC_PLUS (str): FULL COMBO SHINY 类型 "fsp"。
        FULL_SYNC_DX (str): FULL COMBO DX 类型 "fsd"。
        FULL_SYNC_DX_PLUS (str): FULL COMBO DX SHINY 类型 "fsdp"。
        SYNC (str): SYNC 类型 "sync"。
    """

    FULL_SNYC = "fs"  # FULL COMBO
    FULL_SNYC_PLUS = "fsp"  # FULL COMBO SHINY
    FULL_SYNC_DX = "fsd"  # FULL COMBO DX
    FULL_SYNC_DX_PLUS = "fsdp"  # FULL COMBO DX SHINY
    SYNC = "sync"  # SYNC


class FCType(Enum):
    """FC 类型枚举类。

    Attributes:
        FULL_COMBO (str): FULL COMBO 类型 "fc"。
        FULL_COMBO_PLUS (str): FULL COMBO SHINY 类型 "fcp"。
        ALL_PERFECT (str): ALL PERFECT 类型 "ap"。
        ALL_PERFECT_PLUS (str): ALL PERFECT SHINY 类型 "app"。
    """

    FULL_COMBO = "fc"  # FULL COMBO
    FULL_COMBO_PLUS = "fcp"  # FULL COMBO SHINY
    ALL_PERFECT = "ap"  # ALL PERFECT
    ALL_PERFECT_PLUS = "app"  # ALL PERFECT SHINY

    # 版本映射字典
