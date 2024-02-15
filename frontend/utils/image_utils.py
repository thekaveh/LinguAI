import base64

class ImageUtils:
    @staticmethod
    def image_to_base64(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
        
    @staticmethod
    def base64_to_image(base64_string, image_path):
        with open(image_path, "wb") as image_file:
            image_file.write(base64.b64decode(base64_string))