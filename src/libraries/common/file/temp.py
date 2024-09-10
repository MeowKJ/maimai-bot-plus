import os
import tempfile
from config import TEMP_FOLDER
from PIL import Image


class TempFileManager:
    """A class for managing temporary files within a specified directory."""

    def __init__(self) -> None:
        """Initializes the TempFileManager with a specified temporary directory.

        If the directory specified by TEMP_FOLDER does not exist, it is created.

        Attributes:
            temp_dir (str): Path to the temporary directory.
        """
        if not os.path.exists(TEMP_FOLDER):
            os.makedirs(TEMP_FOLDER)
        self.temp_dir: str = TEMP_FOLDER

    def create_temp_file(
        self, data: str = None, suffix: str = "", prefix: str = "temp_", dir: str = None
    ) -> tuple[str, str]:
        """Creates a temporary file and optionally writes data to it.

        Args:
            data (str, optional): Data to write to the temporary file. Defaults to None.
            suffix (str, optional): Suffix for the temporary file name. Defaults to "".
            prefix (str, optional): Prefix for the temporary file name. Defaults to "temp_".
            dir (str, optional): Directory in which to create the file. Defaults to None, which means TEMP_FOLDER is used.

        Returns:
            tuple[str, str]: A tuple containing the full path to the file and the file name.
        """
        temp_file = tempfile.NamedTemporaryFile(
            delete=False, suffix=suffix, prefix=prefix, dir=dir or self.temp_dir
        )
        if data:
            with open(temp_file.name, "w") as f:
                f.write(data)
        file_name: str = os.path.basename(temp_file.name)
        return temp_file.name, file_name

    def create_temp_image_file(
        self,
        image: Image.Image,
        suffix: str = ".png",
        prefix: str = "temp_image_",
        quality: int = 80,
    ) -> tuple[str, str]:
        """Creates a temporary file from a PIL.Image object and saves it as an image file.

        Args:
            image (Image.Image): The PIL.Image object to save.
            suffix (str, optional): Suffix for the temporary file name. Defaults to ".png".
            prefix (str, optional): Prefix for the temporary file name. Defaults to "temp_image_".

        Returns:
            tuple[str, str]: A tuple containing the full path to the file and the file name.
        """
        temp_file = tempfile.NamedTemporaryFile(
            delete=False, suffix=suffix, prefix=prefix, dir=self.temp_dir
        )
        if suffix == ".png":
            image.save(temp_file.name, "PNG")
        elif suffix == ".jpg":
            # OSError: cannot write mode RGBA as JPEG
            if image.mode == "RGBA":
                image = image.convert("RGB")
            image.save(temp_file.name, "JPEG", quality=quality)
        else:
            image.save(temp_file.name)
        file_name: str = os.path.basename(temp_file.name)
        return temp_file.name, file_name

    def read_temp_file(self, file_path: str) -> str:
        """Reads the content of a temporary file.

        Args:
            file_path (str): The full path to the file to be read.

        Returns:
            str: The content of the file.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return f.read()
        else:
            raise FileNotFoundError(f"Temporary file {file_path} does not exist.")

    def delete_temp_file(self, file_path: str) -> None:
        """Deletes a specified temporary file.

        Args:
            file_path (str): The full path to the file to be deleted.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            raise FileNotFoundError(f"Temporary file {file_path} does not exist.")

    def cleanup(self) -> None:
        """Cleans up the temporary directory by deleting all files within it."""
        for temp_file in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, temp_file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print(f"All temporary files in {self.temp_dir} have been deleted.")


# 示例用法
# if __name__ == "__main__":
#     from PIL import Image

#     temp_manager = TempFileManager()

#     # 创建一个临时文件并写入数据，同时获取路径和文件名
#     file_path, file_name = temp_manager.create_temp_file(data="Hello, temporary world!")
#     print(f"Temporary file created at: {file_path} with name: {file_name}")

#     # 创建一个临时图像文件
#     example_image = Image.new("RGB", (100, 100), color=(73, 109, 137))
#     image_path, image_name = temp_manager.create_temp_image_file(example_image)
#     print(f"Temporary image file created at: {image_path} with name: {image_name}")

#     # 读取临时文件的数据
#     content = temp_manager.read_temp_file(file_path)
#     print(f"Content of the temporary file: {content}")

#     # 删除临时文件
#     temp_manager.delete_temp_file(file_path)
#     print(f"Temporary file {file_path} deleted.")

#     # 清理临时目录
#     temp_manager.cleanup()
