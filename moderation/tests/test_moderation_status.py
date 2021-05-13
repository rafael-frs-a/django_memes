import pytest
from time import sleep
from django.forms.models import modelform_factory
from django.db.utils import IntegrityError
from posts.models import Post
from .test_utils import create_moderator_test_user, create_test_post, create_test_denial_reason
from ..models import ModerationStatus


def get_form_class():
    fields = ['post', 'moderator_moderating',
              'result', 'moderator_result', 'denial_reason']
    return modelform_factory(ModerationStatus, fields=fields)


def perform_failed_save(post, form_data):
    initial_count = post.status.count()
    initial_moderation_status = post.moderation_status
    form = get_form_class()(data=form_data)

    with pytest.raises(ValueError):
        form.save()

    assert not form.is_valid()
    assert post.status.count() == initial_count
    assert post.moderation_status == initial_moderation_status


def perform_successful_save(post, form_data, post_status, approved=False):
    initial_count = ModerationStatus.objects.count()
    form = get_form_class()(data=form_data)
    assert form.is_valid()
    form.save()
    assert ModerationStatus.objects.count() == initial_count + 1
    post = Post.objects.filter(id=post.id).first()
    assert post.moderation_status == post_status
    assert not approved or post.approved_at


@pytest.mark.django_db
def test_moderating_missing_post(valid_user_1):
    user = create_moderator_test_user(valid_user_1)
    status = ModerationStatus(moderator_moderating=user, moderator_result=user)

    with pytest.raises(IntegrityError):
        status.save()


@pytest.mark.django_db
def test_moderating_missing_moderator_result(valid_user_1, valid_image_file):
    user = create_moderator_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file)
    form_data = {
        'post': post,
        'result': ModerationStatus.MODERATING,
        'moderator_moderating': user
    }

    perform_failed_save(post, form_data)


@pytest.mark.django_db
def test_moderating_different_moderators(valid_user_1, valid_user_2, valid_image_file):
    user1 = create_moderator_test_user(valid_user_1)
    user2 = create_moderator_test_user(valid_user_2)
    post = create_test_post(user1, valid_image_file)
    form_data = {
        'post': post,
        'result': ModerationStatus.MODERATING,
        'moderator_moderating': user1,
        'moderator_result': user2
    }

    perform_failed_save(post, form_data)


@pytest.mark.django_db
def test_moderating_post_already_moderating(valid_user_1, valid_user_2, valid_image_file):
    user1 = create_moderator_test_user(valid_user_1)
    user2 = create_moderator_test_user(valid_user_2)
    post = create_test_post(user1, valid_image_file)
    form_data = {
        'post': post,
        'result': ModerationStatus.MODERATING,
        'moderator_moderating': user1,
        'moderator_result': user1
    }

    perform_successful_save(post, form_data, ModerationStatus.MODERATING)
    form_data = {
        'post': post,
        'result': ModerationStatus.MODERATING,
        'moderator_moderating': user2,
        'moderator_result': user2
    }

    perform_failed_save(post, form_data)


@pytest.mark.django_db
def test_moderator_moderating_more_one_post(valid_user_1, valid_image_file):
    user = create_moderator_test_user(valid_user_1)
    post1 = create_test_post(user, valid_image_file)
    post2 = create_test_post(user, valid_image_file)
    assert user.posts.count() == 2
    form_data = {
        'post': post1,
        'result': ModerationStatus.MODERATING,
        'moderator_moderating': user,
        'moderator_result': user
    }

    perform_successful_save(post1, form_data, ModerationStatus.MODERATING)
    form_data = {
        'post': post2,
        'result': ModerationStatus.MODERATING,
        'moderator_moderating': user,
        'moderator_result': user
    }

    perform_failed_save(post2, form_data)


@pytest.mark.django_db
def test_moderating_with_denial_reason(client, valid_user_1, valid_image_file, valid_denial_reason_1):
    user = create_moderator_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file)
    reason = create_test_denial_reason(valid_denial_reason_1)
    form_data = {
        'post': post,
        'result': ModerationStatus.MODERATING,
        'moderator_moderating': user,
        'moderator_moderator': user,
        'denial_reason': reason
    }

    perform_failed_save(post, form_data)


@pytest.mark.django_db
def test_approved_missing_moderator_result(client, valid_user_1, valid_image_file):
    user = create_moderator_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file)
    form_data = {
        'post': post,
        'result': ModerationStatus.APPROVED
    }

    perform_failed_save(post, form_data)


@pytest.mark.django_db
def test_approved_with_denial_reason(client, valid_user_1, valid_image_file, valid_denial_reason_1):
    user = create_moderator_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file)
    reason = create_test_denial_reason(valid_denial_reason_1)
    form_data = {
        'post': post,
        'result': ModerationStatus.APPROVED,
        'moderator_result': user,
        'denial_reason': reason
    }

    perform_failed_save(post, form_data)


@pytest.mark.django_db
def test_denied_missing_moderator_result(client, valid_user_1, valid_image_file, valid_denial_reason_1):
    user = create_moderator_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file)
    reason = create_test_denial_reason(valid_denial_reason_1)
    form_data = {
        'post': post,
        'result': ModerationStatus.DENIED,
        'denial_reason': reason
    }

    perform_failed_save(post, form_data)


@pytest.mark.django_db
def test_denied_missing_denial_reason(client, valid_user_1, valid_image_file):
    user = create_moderator_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file)
    form_data = {
        'post': post,
        'result': ModerationStatus.DENIED,
        'moderator_result': user
    }

    perform_failed_save(post, form_data)


@pytest.mark.django_db
def test_approved_with_moderator_moderating(client, valid_user_1, valid_image_file):
    user = create_moderator_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file)
    form_data = {
        'post': post,
        'result': ModerationStatus.APPROVED,
        'moderator_moderating': user,
        'moderator_result': user
    }

    perform_failed_save(post, form_data)


@pytest.mark.django_db
def test_denied_with_moderator_moderating(client, valid_user_1, valid_image_file, valid_denial_reason_1):
    user = create_moderator_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file)
    reason = create_test_denial_reason(valid_denial_reason_1)
    form_data = {
        'post': post,
        'result': ModerationStatus.DENIED,
        'moderator_moderating': user,
        'moderator_result': user,
        'denial_reason': reason
    }

    perform_failed_save(post, form_data)


@pytest.mark.django_db
def test_two_identical_approved(client, valid_user_1, valid_image_file):
    user = create_moderator_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file)
    form_data = {
        'post': post,
        'result': ModerationStatus.APPROVED,
        'moderator_result': user
    }

    perform_successful_save(post, form_data, Post.APPROVED, True)
    perform_failed_save(post, form_data)


@pytest.mark.django_db
def test_two_identical_denied(client, valid_user_1, valid_image_file, valid_denial_reason_1):
    user = create_moderator_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file)
    reason = create_test_denial_reason(valid_denial_reason_1)
    form_data = {
        'post': post,
        'result': ModerationStatus.DENIED,
        'moderator_result': user,
        'denial_reason': reason
    }

    perform_successful_save(post, form_data, Post.DENIED)
    perform_failed_save(post, form_data)


@pytest.mark.django_db
def test_successful_post_status(client, valid_user_1, valid_image_file, valid_denial_reason_1):
    user = create_moderator_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file)
    reason = create_test_denial_reason(valid_denial_reason_1)

    form_data = {
        'post': post,
        'result': ModerationStatus.MODERATING,
        'moderator_moderating': user,
        'moderator_result': user
    }

    perform_successful_save(post, form_data, Post.MODERATING)
    status_moderating = post.status.order_by('-created_at').first()
    sleep(1)

    form_data = {
        'post': post,
        'result': ModerationStatus.DENIED,
        'moderator_result': user,
        'denial_reason': reason
    }

    perform_successful_save(post, form_data, Post.DENIED)
    status_denied = post.status.order_by('-created_at').first()
    sleep(1)

    form_data = {
        'post': post,
        'result': ModerationStatus.APPROVED,
        'moderator_result': user
    }

    perform_successful_save(post, form_data, Post.APPROVED, True)
    status_approved = post.status.order_by('-created_at').first()

    status_approved.delete()
    post = Post.objects.filter(id=post.id).first()
    assert post.moderation_status == Post.DENIED

    status_denied.delete()
    post = Post.objects.filter(id=post.id).first()
    assert post.moderation_status == Post.MODERATING

    status_moderating.delete()
    post = Post.objects.filter(id=post.id).first()
    assert post.moderation_status == Post.WAITING_MODERATION
    assert post.status.count() == 0
