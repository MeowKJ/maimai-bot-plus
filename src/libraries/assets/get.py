from pathlib import Path
from enum import Enum
import aiohttp
import requests
from botpy import logger
from config import ASSETS_URL


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
    TROPHY = "/assets/trophy/"
    PLATE = "/assets/plate/"
    BG = "/assets/bg/"
    IMAGES = "/assets/images/"
    AVATAR = "/assets/avatar/"


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

    def get(self, asset_type: AssetType, param_value: str) -> str:
        """
        获取资产 (同步)
        """
        # Automatically add .png suffix for IMAGES type if not present
        if asset_type == AssetType.IMAGES and not param_value.lower().endswith(
            (".png", ".jpg", ".jpeg", ".gif")
        ):
            param_value += ".png"

        file_name = (
            param_value if asset_type == AssetType.IMAGES else f"{param_value}.png"
        )
        local_file_path = Path(self.assets_folder, asset_type.name.lower(), file_name)

        if local_file_path.exists():
            logger.debug(f"[ASSETS] 资产已存在：{local_file_path}")
            return str(local_file_path)

        asset_url = f"{self.base_url}{asset_type.value}{param_value}"
        try:
            self.download_file(asset_url, local_file_path, self.proxy)
        except requests.exceptions.RequestException as e:
            logger.warning(f"[ASSETS] 下载文件失败：{asset_url}, 错误信息：{e}")
        return str(local_file_path)

    async def get_async(self, asset_type: AssetType, param_value: str) -> str:
        """
        获取资产 (异步)
        """
        # Automatically add .png suffix for IMAGES type if not present
        if asset_type == AssetType.IMAGES and not param_value.lower().endswith(
            (".png", ".jpg", ".jpeg", ".gif")
        ):
            param_value += ".png"

        file_name = (
            param_value if asset_type == AssetType.IMAGES else f"{param_value}.png"
        )
        local_file_path = Path(self.assets_folder, asset_type.name.lower(), file_name)

        if local_file_path.exists():
            logger.debug(f"[ASSETS] 资产已存在：{local_file_path}")
            return str(local_file_path)

        asset_url = f"{self.base_url}{asset_type.value}{param_value}"
        try:
            await self.download_file_async(asset_url, local_file_path, self.proxy)
        except aiohttp.ServerTimeoutError:
            logger.warning(f"[ASSETS] 下载文件超时：{asset_url}")
        return str(local_file_path)

    @staticmethod
    def download_file(url: str, save_path: str, proxy=None):
        """
        从URL下载文件 (同步)
        """
        logger.info(f"[ASSETS] 下载文件：{url}")
        try:
            response = requests.get(
                url, proxies={"http": proxy, "https": proxy}, timeout=60
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
    async def download_file_async(url: str, save_path: str, proxy=None):
        """
        从URL下载文件 (异步)
        """
        logger.info(f"[ASSETS] 下载文件：{url}")
        async with aiohttp.ClientSession(conn_timeout=60) as session:
            async with session.get(url, proxy=proxy) as response:
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
