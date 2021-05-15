import io
from django.core.files.storage import default_storage
from google.cloud import vision


def _annotate(post):
    if not default_storage.exists(post.meme_file.name):
        return None

    client = vision.ImageAnnotatorClient()
    path = post.meme_file.url

    if path.startswith('http') or path.startswith('gs:'):
        image = vision.Image()
        image.source.image_uri = path

    else:
        with io.open(post.meme_file.path, 'rb') as img:
            content = img.read()

        image = vision.Image(content=content)

    response = client.text_detection(image=image)
    return response.full_text_annotation


def get_post_text(post):
    result = _annotate(post)

    if result and result.text:
        return result.text.replace('\n', ' ')

    return None
