import string
from io import BytesIO
from captcha.image import ImageCaptcha
import random


class CaptchaTools:
    IMAGE_WIDTH = 280
    IMAGE_HEIGHT = 90

    @staticmethod
    def generate_captcha() -> tuple[BytesIO, str]:
        text = CaptchaTools.__generate_code()
        image_captcha = ImageCaptcha(width=CaptchaTools.IMAGE_WIDTH, height=CaptchaTools.IMAGE_HEIGHT)
        data = image_captcha.generate(text)
        bio = BytesIO(data.read())
        bio.seek(0)

        return bio, text

    @staticmethod
    def __generate_code():
        digits = string.digits
        return "".join(random.choice(digits) for _ in range(random.randint(5, 6)))
