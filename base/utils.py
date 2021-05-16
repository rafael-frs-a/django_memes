from io import BytesIO
from django.conf import settings
from PIL import Image


def inverse_case(text):
    return ''.join(c.lower() if c.isupper() else c.upper() for c in text)


def resized_img(image, file_object, image_size):
    if settings.TEST_MODE:
        return

    img = Image.open(image)
    img.thumbnail(image_size)
    img_bytes = BytesIO()
    ext = image.name.split('.')[-1]
    ext = 'JPEG' if ext.lower() == 'jpg' else ext
    img.save(img_bytes, format=ext)
    file_object.file = img_bytes
    file_object.size = img_bytes.tell()
