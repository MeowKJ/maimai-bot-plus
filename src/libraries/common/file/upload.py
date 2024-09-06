import os
import aiohttp
from config import IMAGES_SERVER_ADDRESS


async def upload_to_image_server(file_path):
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
                content_type="image/png",  # 根据实际情况设置文件类型
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
