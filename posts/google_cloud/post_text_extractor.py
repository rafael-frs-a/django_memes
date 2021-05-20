from .utils import get_client_image_from_post


def _annotate(post):
    client, image = get_client_image_from_post(post)

    if not client:
        return image

    response = client.text_detection(image=image)
    return response.full_text_annotation


def get_post_text(post):
    result = _annotate(post)

    if result and result.text:
        return result.text.replace('\n', ' ')

    return None
