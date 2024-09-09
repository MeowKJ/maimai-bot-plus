import aiohttp
from botpy import logger
from src.libraries.common.platform.lxns import SongIDConverter
from .enums import *


class UserDifficultyScore:
    # 歌曲ID
    id: int

    # 铺面序号
    level_index: SongLevel

    # 难度等级达成率
    achievement: float

    # 难度等级评价
    rate: SongRateType

    # 难度等级ra分数
    rating: int

    # DX分数
    dx_rating: int


class Notes:
    # 音符总数
    total: int

    # tap音符数
    tap: int

    # hold音符数
    hold: int

    # slide音符数
    slide: int

    # touch音符数
    touch: int

    # break音符数
    break_: int

    def __init__(self, *args, **kwargs):
        self.total = kwargs.get("total", 0)
        self.tap = kwargs.get("tap", 0)
        self.hold = kwargs.get("hold", 0)
        self.slide = kwargs.get("slide", 0)
        self.touch = kwargs.get("touch", 0)
        self.break_ = kwargs.get("break_", 0)
        if self.total == 0 and self.tap != 0:
            self.total = self.tap + self.hold + self.slide + self.touch + self.break_

    def caculate_dx_score(self) -> int:
        """
        计算DX铺面分数

        Returns:
            int: DX铺面分数
        """
        return self.total * 3

    def to_dict(self):
        return {
            "total": self.total,
            "tap": self.tap,
            "hold": self.hold,
            "slide": self.slide,
            "touch": self.touch,
            "break": self.break_,
        }


class BuddyNotes:
    left: int
    right: int


class SongDifficulty:
    # 难度等级(定数)
    level: float

    # 难度等级标签(13+)
    level_lable: str

    # 难度等级索引(0 Basic, 1 Advanced, 2 Expert, 3 Master, 4 Re:Master)
    level_index: SongLevel

    # 难度等级名称(BASIC, ADVANCED, EXPERT, MASTER, RE:MASTER)
    level_text: SongLevelText

    # 铺面作者
    note_designer: str = "-"

    # 最高DX分数
    dx_rating_max: int = 0

    # 音符
    notes: Notes

    # 玩家成绩
    user_socre: UserDifficultyScore

    def __init__(self, *args, **kwargs):
        self.level = kwargs.get("level", 0)
        self.level_index = kwargs.get("level_index", SongLevel.BASIC)
        self.note_designer = kwargs.get("note_designer", "-")

        # level_lable
        # 如果没有传入level_lable,则通过level计算
        if "level_lable" in kwargs:
            self.level_lable = kwargs.get("level_lable", "")
        else:
            # 通过level计算level_lable, 如果小数位大于6，则换成➕
            if self.level - int(self.level) > 0.6:
                self.level_lable = str(int(self.level)) + "+"
            else:
                self.level_lable = str(int(self.level))

        # level_text
        # 如果没有传入level_text,则通过level_index计算
        if "level_text" in kwargs:
            self.level_text = kwargs.get("level_text", SongLevelText.BASIC)
        else:
            self.level_text = SongLevelTextMap[self.level_index]

        # note
        # 通过notes计算最大DX分数
        if "notes" in kwargs:
            self.notes = kwargs.get("notes", Notes())
            self.dx_rating_max = self.notes.caculate_dx_score()


class SongDifficultyUtage:
    # 铺面属性
    kanji: str

    # 铺面描述
    description: str

    # 是否为Buddy铺面
    is_buddy: bool

    # 铺面Note数
    notes: Notes | BuddyNotes


class Song:
    # 歌曲ID
    id: int

    # 歌曲名
    title: str

    # 歌手名
    artist: str

    # BPM
    bpm: int

    # 曲目分类
    genre: str

    # 曲目版本
    version: str

    # 是否被禁用
    disabled: bool

    # 是否为新曲目
    isnew: bool

    # 是否含有Re:MASTER铺面
    has_re_master: bool

    # 歌曲类型
    song_type: SongType

    # 获取地图
    _map: str = ""

    # 铺面列表
    difficulties: List[SongDifficulty]

    # UTAGE铺面
    difficulties_utage: SongDifficultyUtage

    def __init__(self, id):
        self.id = id
        if self.id < 10000:
            self.song_type = SongType.STANDARD
        elif self.id < 100000:
            self.song_type = SongType.DX
        else:
            self.song_type = SongType.UTAGE
        self.difficulties = []
        self.difficulties_utage = None

    async def enrich(self):
        """
        丰富歌曲信息
        """
        lxns_id = SongIDConverter.common_to_lxns_songid(self.id)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://maimai.lxns.net/api/v0/maimai/song/{lxns_id}"
            ) as response:
                if response.status == 200:
                    song = await response.json()
                else:
                    return False
        self.title = song["title"]
        self.artist = song["artist"]
        self.bpm = song["bpm"]
        self.genre = song["genre"]
        self.version = song["version"]
        logger.info(f"[LMAIMAI] 歌曲信息: {self.title} - {self.genre}")
        if "map" in song and self.song_type == SongType.DX:
            self._map = song["map"]

        # TODO: UTAGE铺面
        for i, song_info in enumerate(song["difficulties"][self.song_type.value]):

            notes = Notes(
                total=song_info["notes"]["total"],
                tap=song_info["notes"]["tap"],
                hold=song_info["notes"]["hold"],
                slide=song_info["notes"]["slide"],
                touch=song_info["notes"]["touch"],
                break_=song_info["notes"]["break"],
            )

            difficulty = SongDifficulty(
                # 定数
                level=song_info["level_value"],
                # 难度标签
                level_lable=song_info["level"],
                # 难度索引
                level_index=song_info["difficulty"],
                # 铺面作者
                note_designer=song_info["note_designer"],
                # 版本
                version=song_info["version"],
                # 音符
                notes=notes,
            )

            self._append_difficulty(difficulty)
        return True

    def _append_difficulty(self, difficulty: SongDifficulty):
        """
        添加铺面

        Args:
            difficulty (SongDifficulty): 铺面
        """
        self.difficulties.append(difficulty)
