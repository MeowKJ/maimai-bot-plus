from .enums import *


class UserInfo:
    username: str
    avatar: str
    rating: int
    course_rank: int
    class_rank: int
    trophy: str
    nameplate_id: int
    frame_id: int

    def __init__(
        self,
        username: str,
        avatar: str,
        rating: int,
        course_rank: int,
        class_rank: int,
        trophy: str,
        nameplate_id: int,
        frame_id: int,
    ):
        self.username = username
        self.avatar = avatar
        self.rating = rating
        self.course_rank = course_rank
        self.class_rank = class_rank
        self.trophy = trophy
        self.nameplate_id = nameplate_id
        self.frame_id = frame_id


class UserDifficultyScore:

    # 铺面序号
    level_index: SongLevel

    # 难度等级达成率
    achievements: float

    # 难度等级评价
    rate: SongRateType

    # 难度等级ra分数
    rating: int

    # fc
    fc: FCType = FCType.NONE

    # fs
    fs: FSType = FSType.NONE

    # 铺面分数
    dx_score: int

    def __init__(self, *args, **kwargs):
        self.level_index = kwargs.get("level_index", SongLevel.BASIC)
        self.achievements = kwargs.get("achievements", 0)
        self.rate = kwargs.get("rate", SongRateType.D)
        self.rating = kwargs.get("rating", 0)
        self.fc = kwargs.get("fc", FCType.NONE)
        self.fs = kwargs.get("fs", FSType.NONE)
        self.dx_score = kwargs.get("dx_score", 0)


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
    # 乐曲 ID
    id: int

    # 乐曲类型
    song_type: SongType

    # 乐曲名称
    title: str

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
    user_score: UserDifficultyScore = None

    def __init__(self, *args, **kwargs):
        self.level = kwargs.get("level", 0)
        self.level_index = kwargs.get("level_index", SongLevel.BASIC)
        self.note_designer = kwargs.get("note_designer", "-")
        self.id = kwargs.get("id", 0)
        self.title = kwargs.get("title", "")

        if "song_type" in kwargs:
            self.song_type = kwargs.get("song_type", SongType.STANDARD)
        else:
            if self.id < 10000:
                self.song_type = SongType.STANDARD
            elif self.id < 100000:
                self.song_type = SongType.DX
            else:
                self.song_type = SongType.UTAGE

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

    def get_dx_score_num(self) -> int:
        """
        获取DX分数等级

        Returns:
            int: DX分数
        """

        if self.dx_rating_max and self.user_score.dx_score:
            dx_score_num = self.user_score.dx_score / self.dx_rating_max
            if dx_score_num <= 0.85:
                return 0
            elif dx_score_num <= 0.90:
                return 1
            elif dx_score_num <= 0.93:
                return 2
            elif dx_score_num <= 0.95:
                return 3
            elif dx_score_num <= 0.97:
                return 4
            else:
                return 5
        else:
            return 0


class SongDifficultyUtage:
    # 铺面属性
    kanji: str

    # 铺面描述
    description: str

    # 是否为Buddy铺面
    is_buddy: bool

    # 铺面Note数
    notes: Notes | BuddyNotes
