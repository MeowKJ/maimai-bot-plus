"""
alias
"""

import os
import aiohttp
from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions

from config import IMAGES_SERVER_ADDRESS

from botpy import logger


async def upload_to_imagekit(file_path):
    """
    将本地图片上传到自己的服务器，并返回图片的URL。
    """
    upload_url = f"{IMAGES_SERVER_ADDRESS}/upload/"  # 替换为你的服务器上传接口

    # 打开文件进行上传
    async with aiohttp.ClientSession() as session:
        with open(file_path, "rb") as f:
            # 创建一个 form data
            form_data = aiohttp.FormData()
            form_data.add_field(
                "file",
                f,
                filename=os.path.basename(file_path),
                content_type="image/jpeg",  # 根据实际情况设置文件类型
            )

            # 上传文件到服务器
            async with session.post(upload_url, data=form_data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    # 假设服务器返回的数据结构中有一个 'file_url' 字段
                    url = response_data.get("file_url")
                    return url
                else:
                    raise Exception(f"Failed to upload file: {response.status}")


async def get_alias_by_id(song_id: int) -> str:
    """
    get_alias_by_id

    Args:
        song_id (int): song_id

    Returns:
        str: alias
    """
    total_aliases = []
    url = "https://maimai.lxns.net/api/v0/maimai/alias/list"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:

            if resp.status != 200:
                return
            data = await resp.json()

            aliases = data.get("aliases")
            for i in aliases:
                if i.get("song_id") == song_id:
                    total_aliases += i.get("alias")

    url2 = "https://download.fanyu.site/maimai/alias.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url2) as resp:

            if resp.status != 200:
                return
            data = await resp.json()

            total_aliases += data.get(str(song_id))

    return total_aliases


versions = [
    {id: 0, "title": "maimai", "version": 10000},
    {id: 1, "title": "maimai PLUS", "version": 11000},
    {id: 2, "title": "GreeN", "version": 12000},
    {id: 3, "title": "GreeN PLUS", "version": 13000},
    {id: 4, "title": "ORANGE", "version": 14000},
    {id: 5, "title": "ORANGE PLUS", "version": 15000},
    {id: 6, "title": "PiNK", "version": 16000},
    {id: 7, "title": "PiNK PLUS", "version": 17000},
    {id: 8, "title": "MURASAKi", "version": 18000},
    {id: 9, "title": "MURASAKi PLUS", "version": 18500},
    {id: 10, "title": "MiLK", "version": 19000},
    {id: 11, "title": "MiLK PLUS", "version": 19500},
    {id: 12, "title": "FiNALE", "version": 19900},
    {id: 13, "title": "舞萌DX", "version": 20000},
    {id: 15, "title": "舞萌DX 2021", "version": 21000},
    {id: 17, "title": "舞萌DX 2022", "version": 22000},
    {id: 19, "title": "舞萌DX 2023", "version": 23000},
    {id: 21, "title": "舞萌DX 2024", "version": 24000},
]


def get_version_name(version_code):
    """
    利用上面定义的版本信息查找对应的版本范围，并返回相应的版本名称
    """
    # 确保版本列表是按版本号排序的
    sorted_versions = sorted(versions, key=lambda x: x["version"])

    for i, version in enumerate(sorted_versions):
        # 如果是最后一个版本或版本号在当前和下一个版本之间
        if (
            i == len(sorted_versions) - 1
            or version_code < sorted_versions[i + 1]["version"]
        ):
            return version["title"]

    return "未知版本"  # 如果没有找到匹配的版本，返回未知版本


async def translate_to_chinese(text, source_language="en"):
    """
    将日文或英文文本翻译成中文，使用不需要认证的免费翻译 API。
    默认从英文翻译，如果提供 source_language 参数则使用指定语言。
    """
    if not text:
        return ""

    endpoint = "https://api.mymemory.translated.net/get"

    params = {
        "q": text,
        "langpair": f"{source_language}|zh-CN",  # Translate from the specified source language to Simplified Chinese
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint, params=params) as response:
            if response.status == 200:
                data = await response.json()
                if "responseData" in data:
                    translated_text = data["responseData"]["translatedText"]
                    return translated_text
                else:
                    logger.error(f"Translation error: {data}")
                    return ""
            else:
                logger.error(f"Translation failed with status: {response.status}")
                return ""
