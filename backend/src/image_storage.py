import os
import uuid

from PIL.Image import Image

from src import config


class ImageStorage:
    @classmethod
    async def save(cls, image: Image) -> str:
        if image.mode == "RGBA":
            image = image.convert("RGB")

        file_name = f"{uuid.uuid4()}.jpeg"
        path = config.STORAGE_PATH / file_name

        image.save(path, format="jpeg")
        return f"/storage/{file_name}"

    @staticmethod
    async def delete_image(image_path: str) -> None:
        os.remove(image_path)
