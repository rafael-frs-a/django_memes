import io
from django.core.files.storage import default_storage
from google.cloud import vision


def _annotate(post):
    if not default_storage.exists(post.meme_file.name):
        return None

    client = vision.ImageAnnotatorClient()

    with io.open(post.meme_file.path, 'rb') as img:
        content = img.read()

    image = vision.Image(content=content)
    response = client.web_detection(image=image)
    return response.web_detection


def get_post_tags(post):
    result = _annotate(post)

    if result and result.best_guess_labels:
        return [_.label for _ in result.best_guess_labels if _.label]

    return None
