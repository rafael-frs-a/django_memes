import pytest
from django.db.utils import IntegrityError
from .test_utils import create_test_user, create_test_post
from ..models import PostTag, Post


@pytest.mark.django_db
def test_tags(client, valid_user_1, valid_image_file_1):
    user = create_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file_1)
    assert not post.meme_labels
    assert post.tags.count() == 0
    tags = sorted(['first tag', 'second tag', 'third tag'])

    for tag in tags:
        post_tag = PostTag(post=post, description=tag)
        post_tag.save()

    post = Post.objects.filter(id=post.id).first()
    assert post.tags.count() == len(tags)
    assert post.meme_labels == ' '.join(tags)
    tag = tags.pop()
    post_tag = post.tags.filter(description=tag).first()
    post_tag.delete()
    post = Post.objects.filter(id=post.id).first()
    assert post.tags.count() == len(tags)
    assert post.meme_labels == ' '.join(tags)
    tag = tags[0]
    post_tag = post.tags.filter(description=tag).first()
    post_tag.description = 'modified tag'
    post_tag.save()
    tags[0] = post_tag.description
    tags.sort()
    post = Post.objects.filter(id=post.id).first()
    assert post.tags.count() == len(tags)
    assert post.meme_labels == ' '.join(tags)


@pytest.mark.django_db
def test_duplicated_tags(client, valid_user_1, valid_image_file_1):
    user = create_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file_1)
    tag = 'test tag'
    post_tag = PostTag(post=post, description=tag)
    post_tag.save()
    assert post.tags.count() == 1

    with pytest.raises(IntegrityError):
        post_tag = PostTag(post=post, description=tag)
        post_tag.save()
