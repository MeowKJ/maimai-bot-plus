
class Song:
    # 歌曲ID
    id: int

    # 歌曲名
    title: str

    # 歌手名
    artist: str

    # BPM
    bpm: int

    # 难度等级
    level_index: int

    # 曲目分类
    genre: str

    # 曲目版本
    version: str

    # 是否被禁用
    disabled: bool

    # 是否为新曲目
    isnew: bool

class Difficulty:
    # 难度等级
    level: int

    # 难度等级索引
    level_index: int

    # 难度等级名称
    level_name: str

    # 难度等级颜色
    level_color: str

    # 难度等级描述
    level_description: str

    # 难度等级评价
    level_rating: str

    # 难度等级评价颜色
    level_rating_color: str

    # 难度等级评价描述
    level_rating_description: str

    # 难度等级评价描述颜色