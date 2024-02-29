import base64

from PIL import Image
from io import BytesIO


class ImageUtils:
    @staticmethod
    def image_bytes_to_base64(image_bytes):
        return base64.b64encode(image_bytes).decode("utf-8")

    @staticmethod
    def image_file_to_base64(image_path):
        with open(image_path, "rb") as image_file:
            return ImageUtils.image_bytes_to_base64(image_file.read())

    @staticmethod
    def base64_to_image(base64_string, image_path):
        with open(image_path, "wb") as image_file:
            image_file.write(base64.b64decode(base64_string))

    @staticmethod
    def uploaded_image_to_base64_image_url(uploaded_image):
        if uploaded_image is not None and uploaded_image.type in [
            "image/png",
            "image/jpeg",
            "image/jpg",
            "image/gif",
            "image/bmp",
            "image/webp",
        ]:
            image_base64 = ImageUtils.image_bytes_to_base64(uploaded_image.getvalue())

            return f"data:{uploaded_image.type};base64,{image_base64}"
        else:
            return None
