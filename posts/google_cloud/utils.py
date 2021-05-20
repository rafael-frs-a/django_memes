import io
from django.core.files.storage import default_storage
from google.cloud import vision


def get_client_image_from_post(post):
    if not default_storage.exists(post.meme_file.name):
        return None, None

    client = vision.ImageAnnotatorClient()
    path = post.meme_file.url

    if path.startswith('http') or path.startswith('gs:'):
        image = vision.Image()
        image.source.image_uri = path

    else:
        with io.open(post.meme_file.path, 'rb') as img:
            content = img.read()

        image = vision.Image(content=content)

    return client, image
