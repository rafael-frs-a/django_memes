from enum import Enum
from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.files.storage import default_storage
from .google_cloud.post_labeller import get_post_tags
from .google_cloud.post_text_extractor import get_post_text

logger = get_task_logger(__name__)


class LabelPostResponses(Enum):
    SUCCESS = 0
    POST_NOT_FOUND = 1
    POST_FILE_NOT_FOUND = 2
    POST_NOT_APPROVED = 3
    POST_ALREADY_LABELLED = 4


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 2}, default_retry_delay=5 * 60)
def get_post_labels(id):
    from .models import Post, PostTag
    post = Post.objects.filter(id=id).first()

    if not post:
        logger.info(f'Post with id {id} not found...')
        return LabelPostResponses.POST_NOT_FOUND.name

    if not default_storage.exists(post.meme_file.name):
        logger.info(f'File {post.meme_file.name} not found...')
        return LabelPostResponses.POST_FILE_NOT_FOUND.name

    if post.moderation_status != Post.APPROVED:
        logger.info(f'Post with id {id} not approved...')
        return LabelPostResponses.POST_NOT_APPROVED.name

    if post.meme_labelled:
        logger.info(f'Post with id {id} already labelled...')
        return LabelPostResponses.POST_ALREADY_LABELLED.name

    tags = set(get_post_tags(post))
    post.meme_text = get_post_text(post)
    post.meme_labelled = True
    post.save()

    for tag in tags:
        post_tag = PostTag(post=post, description=tag)
        post_tag.save()

    return LabelPostResponses.SUCCESS.name
