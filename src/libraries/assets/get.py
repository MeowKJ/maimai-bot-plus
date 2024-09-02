import time
import json
from pathlib import Path
from enum import Enum
import aiohttp
import requests
from botpy import logger
from config import ASSETS_URL
from src.libraries.common.platform.lxns import SongIDConverter


class AssetType(Enum):
    """
    AssetType
    枚举类型
    """

    COVER = "/assets/cover/"
    RANK = "/assets/rank/"
    BADGE = "/assets/badge/"
    COURSE_RANK = "/assets/course_rank/"
    CLASS_RANK = "/assets/class_rank/"
    RATING = "/assets/rating/"
    PLATE = "/assets/plate/"
    IMAGES = "/assets/images/"
    AVATAR = "/assets/avatar/"
    ONGEKI = "/assets/ongeki/"
    SONGINFO = "/assets/songinfo/"
    JSON = "/assets/json/"


class JSONType(Enum):
    """
    JSONType
    枚举类型
    """

    DIVING_FISH_SONGS_INFO = "https://www.diving-fish.com/api/maimaidxprober/music_data"
    LXNS_SONGS_INFO = "https://maimai.lxns.net/api/v0/maimai/song/list?notes=true"
    ALIAS = "https://download.fanyu.site/maimai/alias.json"


class Assets:
    """
    资产类
    """

    _instance = None

    def __new__(
        cls, base_url: str = None, assets_folder: str = None, proxy: str = None
    ):
        if cls._instance is None:
            cls._instance = super(Assets, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, base_url: str, assets_folder: str, proxy: str = None) -> None:
        if self._initialized:
            return
        self.base_url = base_url
        self.assets_folder = assets_folder
        self.proxy = proxy
        self._initialized = True

    def get(self, asset_type: AssetType, param_value: str, get_args="") -> str:
        """
        获取资产 (同步)
        """
        param_value = str(param_value)
        if asset_type == AssetType.COVER:
            if not param_value.isdigit() and param_value.endswith(".png"):
                param_value = param_value[:-4]
            param_value = str(SongIDConverter.common_to_lxns_songid(int(param_value)))

        if asset_type == AssetType.IMAGES and not param_value.lower().endswith(
            (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp")
        ):
            param_value += ".png"

        file_name = param_value if asset_type == AssetType.IMAGES else f"{param_value}"
        local_file_path = Path(self.assets_folder, asset_type.name.lower(), file_name)

        if local_file_path.exists():
            logger.debug(f"[ASSETS] 资产已存在：{local_file_path}")
            return str(local_file_path)

        asset_url = f"{self.base_url}{asset_type.value}{param_value}"
        try:
            self.download_file(asset_url, local_file_path, self.proxy, get_args)
        except requests.exceptions.RequestException as e:
            logger.warning(f"[ASSETS] 下载文件失败：{asset_url}, 错误信息：{e}")
        return str(local_file_path)

    async def get_async(
        self, asset_type: AssetType, param_value: str, get_args=""
    ) -> str:
        """
        获取资产 (异步)
        """
        param_value = str(param_value)
        if asset_type == AssetType.COVER:
            if not param_value.isdigit() and param_value.endswith(".png"):
                param_value = param_value[:-4]
            param_value = str(SongIDConverter.common_to_lxns_songid(int(param_value)))

        if asset_type == AssetType.IMAGES and not param_value.lower().endswith(
            (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp")
        ):
            param_value += ".png"

        file_name = param_value if asset_type == AssetType.IMAGES else f"{param_value}"
        local_file_path = Path(self.assets_folder, asset_type.name.lower(), file_name)

        if local_file_path.exists():
            logger.debug(f"[ASSETS] 资产已存在：{local_file_path}")
            return str(local_file_path)

        asset_url = f"{self.base_url}{asset_type.value}{param_value}"
        try:
            await self.download_file_async(
                asset_url, local_file_path, self.proxy, get_args
            )
        except aiohttp.ServerTimeoutError:
            logger.warning(f"[ASSETS] 下载文件超时：{asset_url}")
        return str(local_file_path)

    async def get_json(self, json_type: JSONType) -> dict:
        """
        获取JSON数据 (异步)
        """
        local_file_path = Path(
            self.assets_folder, "json", f"{json_type.name.lower()}.json"
        )

        # 检查文件是否存在以及是否过期
        if local_file_path.exists():
            file_mod_time = local_file_path.stat().st_mtime
            current_time = time.time()
            time_diff = current_time - file_mod_time

            # 如果文件在一天内未过期（86400秒=1天）
            if time_diff < 86400:
                logger.info(f"[ASSETS] JSON数据已存在且未过期：{local_file_path}")
                with open(local_file_path, "r") as file:
                    return json.load(file)
            else:
                logger.info(f"[ASSETS] JSON数据已过期，将重新下载：{json_type.value}")

        asset_url = json_type.value
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(asset_url) as response:
                    if response.status != 200:
                        logger.warning(f"[ASSETS] 下载JSON数据失败：{asset_url}")
                        return {}
                    content = await response.json()
                    sava_folder = local_file_path.parent
                    if not sava_folder.exists():
                        sava_folder.mkdir(parents=True)
                    # 保存到本地文件
                    with open(local_file_path, "w") as file:
                        json.dump(content, file)
                    logger.info(
                        f"[ASSETS] 从 {asset_url} 下载并保存JSON数据到 {local_file_path}"
                    )
                    return content
        except aiohttp.ServerTimeoutError:
            logger.warning(f"[ASSETS] 下载JSON数据超时：{asset_url}")
            return {}

    @staticmethod
    def download_file(url: str, save_path: str, proxy=None, get_args=""):
        """
        从URL下载文件 (同步)
        """
        logger.info(f"[ASSETS] 下载文件：{url}")
        try:
            response = requests.get(
                url + get_args, proxies={"http": proxy, "https": proxy}, timeout=60
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.warning(f"[ASSETS] 下载文件失败：{url}, 错误信息：{e}")
            return

        save_folder = Path(save_path).parent
        if not save_folder.exists():
            save_folder.mkdir(parents=True)
        with open(save_path, "wb") as file:
            file.write(response.content)
        logger.info(f"[ASSETS] 从 {url} 下载并保存文件到 {save_path}")

    @staticmethod
    async def download_file_async(url: str, save_path: str, proxy=None, get_args=""):
        """
        从URL下载文件 (异步)
        """
        logger.info(f"[ASSETS] 下载文件：{url}")
        async with aiohttp.ClientSession(conn_timeout=60) as session:
            async with session.get(url + get_args, proxy=proxy) as response:
                if response.status != 200:
                    logger.warning(f"[ASSETS] 下载文件失败：{url}")
                    return
                save_folder = Path(save_path).parent
                if not save_folder.exists():
                    save_folder.mkdir(parents=True)
                content = await response.read()
                with open(save_path, "wb") as file:
                    file.write(content)
                logger.info(f"[ASSETS] 从 {url} 下载并保存文件到 {save_path}")


# 获取 Assets 类的单例实例
assets = Assets(base_url=ASSETS_URL, assets_folder="static")
