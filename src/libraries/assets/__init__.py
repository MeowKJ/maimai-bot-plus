from .get import Assets, AssetType, JSONType

from config import ASSETS_URL

# 获取 Assets 类的单例实例
assets = Assets(base_url=ASSETS_URL, assets_folder="static")
