class SongIDConverter:
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
