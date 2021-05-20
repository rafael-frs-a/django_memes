from .utils import get_client_image_from_post


def _annotate(post):
    client, image = get_client_image_from_post(post)

    if not client:
        return image

    response = client.web_detection(image=image)
    return response.web_detection


def get_post_tags(post):
    result = _annotate(post)

    if result and result.best_guess_labels:
        return [_.label for _ in result.best_guess_labels if _.label]

    return None
