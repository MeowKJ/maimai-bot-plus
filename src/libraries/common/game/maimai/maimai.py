import math

# 定义评级与对应的达成率下限和评级系数
grade_thresholds = [
    {"grade": "SSS+", "min_rate": 100.5000, "coefficient": 22.4},
    {"grade": "SSS", "min_rate": 100.0000, "coefficient": 21.6},
    {"grade": "SS+", "min_rate": 99.5000, "coefficient": 21.1},
    {"grade": "SS", "min_rate": 99.0000, "coefficient": 20.8},
    {"grade": "S+", "min_rate": 98.0000, "coefficient": 20.3},
    {"grade": "S", "min_rate": 97.0000, "coefficient": 20.0},
]


class MaimaiHelper:
    @staticmethod
    def common_to_lxns_songid(song_id: int) -> int:
        """
        将普通歌曲ID转换为LXNS格式的歌曲ID。

        参数:
        song_id (int): 普通歌曲ID

        返回:
        int: LXNS格式的歌曲ID。
        """
        if 10000 <= song_id < 100000:
            return song_id % 10000
        return song_id

    @staticmethod
    def lxns_to_common_songid(song_id: int) -> int:
        """
        将LXNS格式的歌曲ID转换为普通格式的歌曲ID。

        参数:
        song_id (int): LXNS格式的歌曲ID。

        返回:
        int: 普通格式的歌曲ID。
        """
        if 1000 <= song_id < 10000:
            return song_id + 10000
        return song_id

    @staticmethod
    def is_dx(song_id: int) -> bool:
        """
        判断是否为DX曲目。

        参数:
        song_id (int): 歌曲ID。

        返回:
        bool: 是否为DX曲目。
        """
        return song_id > 9999 and song_id < 100000

    @staticmethod
    def is_sd(song_id: int) -> bool:
        """
        判断是否为普通曲目。

        参数:
        song_id (int): 歌曲ID。

        返回:
        bool: 是否为普通曲目。
        """
        return song_id < 10000

    @staticmethod
    def is_utage(song_id: int) -> bool:
        """
        判断是否为宴会场。

        参数:
        song_id (int): 歌曲ID。

        返回:
        bool: 是否为DX曲目。
        """
        return song_id > 99999

    @staticmethod
    def rating_generator(chart_constant):
        """
        生成从 SSS+ 到 S 的 DX Rating 值。

        Args:
            chart_constant (float): 谱面定数。

        Yields:
            Tuple[str, int]: 评级名称与对应的 DX Rating 值。
        """
        for grade in grade_thresholds:
            # 计算 DX Rating，并向下取整
            dx_rating = math.floor(
                chart_constant * (grade["min_rate"] / 100) * grade["coefficient"]
            )
            yield (grade["grade"], dx_rating)
