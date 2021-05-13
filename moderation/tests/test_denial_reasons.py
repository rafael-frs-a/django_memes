import string
import pytest
from urllib.parse import urlencode
from pytest_django.asserts import assertTemplateUsed
from django.urls import reverse
from .test_utils import create_moderator_test_user
from ..models import PostDenialReason, get_total_reasons_moderator


@pytest.mark.django_db
def test_count_posts(valid_user_1, valid_user_2):
    user1 = create_moderator_test_user(valid_user_1)
    user2 = create_moderator_test_user(valid_user_2)
    assert PostDenialReason.objects.count() == 0

    for count in range(1, 5):
        reason = PostDenialReason(description=f'Generical reason {count}')
        reason.save()

    total = count

    for count in range(1, 4):
        reason = PostDenialReason(
            description=f'User 1 reason {count}', moderator=user1)
        reason.save()

    total += count
    assert get_total_reasons_moderator(
        user1) == user1.post_denial_reasons.count()

    for count in range(1, 3):
        reason = PostDenialReason(
            description=f'User 2 reason {count}', moderator=user2)
        reason.save()

    total += count
    assert get_total_reasons_moderator(
        user2) == user2.post_denial_reasons.count()
    assert PostDenialReason.objects.count() == total


@pytest.mark.django_db
def test_reasons_list_view(client, valid_user_1):
    user = create_moderator_test_user(valid_user_1)
    client.force_login(user)
    url = reverse('moderation:denial-reason-list')
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, 'moderation/denial_reason_list.html')


def check_reasons_list_view_pages(client, user, letters, sort):
    url = reverse('moderation:denial-reason-list')
    page = 1

    while True:
        params = {
            'page': page,
            'sort': sort
        }

        querystring = urlencode(params)
        response = client.get(f'{url}?{querystring}')
        page_obj = response.context['page_obj']
        assert page_obj.number == page
        base = response.context['view'].paginate_by * (page - 1)
        reasons = letters[base:base + response.context['view'].paginate_by]
        obj_list = response.context['object_list']

        for idx in range(len(obj_list)):
            assert obj_list[idx].description == reasons[idx]

        if not page_obj.has_next():
            break

        page += 1


@pytest.mark.django_db
def test_reasons_list_view_querystring(client, valid_user_1, valid_user_2):
    user1 = create_moderator_test_user(valid_user_1)
    user2 = create_moderator_test_user(valid_user_2)
    client.force_login(user1)
    letters = list(string.ascii_lowercase)

    for idx in range(len(letters)):
        if idx % 2:
            letters[idx] = letters[idx].upper()

        reason = PostDenialReason(description=letters[idx], moderator=user1)
        reason.save()

    for num in range(1, 10):
        reason = PostDenialReason(description=str(num), moderator=user2)
        reason.save()

    for num in range(num + 1, 15):
        reason = PostDenialReason(description=str(num))
        reason.save()

    assert PostDenialReason.objects.count() == len(letters) + num
    check_reasons_list_view_pages(client, user1, letters, 'description')
    check_reasons_list_view_pages(client, user1, letters[::-1], '-description')


@pytest.mark.django_db
def test_invalid_sort_param(client, valid_user_1):
    user = create_moderator_test_user(valid_user_1)
    client.force_login(user)
    url = reverse('moderation:denial-reason-list')
    invalid_field = 'arokwntaroise'
    assert not hasattr(PostDenialReason, invalid_field)

    params = {
        'page': 1,
        'sort': invalid_field
    }

    querystring = urlencode(params)
    response = client.get(f'{url}?{querystring}')
    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_denial_reason(client, valid_user_1):
    user = create_moderator_test_user(valid_user_1)
    client.force_login(user)
    reason = PostDenialReason(description='test', moderator=user)
    reason.save()
    assert user.post_denial_reasons.count() == 1
    url = reverse('moderation:denial-reason-delete', kwargs={'id': reason.id})
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, 'moderation/denial_reason_delete.html')
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('moderation:denial-reason-list')
    assert user.post_denial_reasons.count() == 0


@pytest.mark.django_db
def test_delete_invalid_reason(client, valid_user_1):
    user = create_moderator_test_user(valid_user_1)
    client.force_login(user)
    url = reverse('moderation:denial-reason-delete', kwargs={'id': 0})
    response = client.get(url)
    assert response.status_code == 404
    response = client.post(url)
    assert response.status_code == 404


def perform_modify_reason_another_user(client, url_name, user_data_1, user_data_2):
    user1 = create_moderator_test_user(user_data_1)
    user2 = create_moderator_test_user(user_data_2)
    client.force_login(user1)
    reason = PostDenialReason(description='test', moderator=user2)
    reason.save()
    assert user2.post_denial_reasons.count() == 1
    url = reverse(url_name, kwargs={'id': reason.id})
    response = client.get(url)
    assert response.status_code == 404
    response = client.post(url)
    assert response.status_code == 404
    assert user2.post_denial_reasons.count() == 1


@pytest.mark.django_db
def test_delete_reason_another_user(client, valid_user_1, valid_user_2):
    perform_modify_reason_another_user(
        client, 'moderation:denial-reason-delete', valid_user_1, valid_user_2)


def perform_modify_reason_no_user(client, url_name, user_data):
    user = create_moderator_test_user(user_data)
    client.force_login(user)
    reason = PostDenialReason(description='test')
    reason.save()
    assert PostDenialReason.objects.count() == 1
    url = reverse(url_name, kwargs={'id': reason.id})
    response = client.get(url)
    assert response.status_code == 404
    response = client.post(url)
    assert response.status_code == 404
    assert PostDenialReason.objects.count() == 1


@pytest.mark.django_db
def test_delete_reason_no_user(client, valid_user_1):
    perform_modify_reason_no_user(
        client, 'moderation:denial-reason-delete', valid_user_1)


def perform_successful_create_reason(client, user_data, reason_data):
    user = create_moderator_test_user(user_data)
    client.force_login(user)
    url = reverse('moderation:denial-reason-create')
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed('moderation/denial_reason_create.html')
    response = client.post(url, reason_data)
    assert response.status_code == 302
    assert response.url == reverse('moderation:denial-reason-list')
    assert user.post_denial_reasons.count() == 1
    assert user.post_denial_reasons.first(
    ).description == reason_data['description']


@pytest.mark.django_db
def test_successful_create_reason(client, valid_user_1, valid_denial_reason_1):
    perform_successful_create_reason(
        client, valid_user_1, {'description': valid_denial_reason_1})


@pytest.mark.django_db
def test_create_repeated_reason_another_user(client, valid_user_1, valid_user_2, valid_denial_reason_1):
    user = create_moderator_test_user(valid_user_2)
    reason = PostDenialReason(
        description=valid_denial_reason_1, moderator=user)
    reason.save()
    assert user.post_denial_reasons.count() == 1
    assert user.post_denial_reasons.first().description == valid_denial_reason_1
    perform_successful_create_reason(
        client, valid_user_1, {'description': valid_denial_reason_1})


def perform_failed_create_reason(client, user_data, reason_data):
    user = create_moderator_test_user(user_data)
    client.force_login(user)
    url = reverse('moderation:denial-reason-create')
    response = client.post(url, reason_data)
    assert response.status_code == 302
    assert response.url == url
    assert user.post_denial_reasons.count() == 0


@pytest.mark.django_db
def test_create_reason_description_missing(client, valid_user_1):
    perform_failed_create_reason(client, valid_user_1, {})


@pytest.mark.django_db
def test_create_reason_short_description(client, valid_user_1, short_denial_reason):
    reason_data = {
        'description': short_denial_reason
    }

    perform_failed_create_reason(client, valid_user_1, reason_data)


@pytest.mark.django_db
def test_create_reason_long_description(client, valid_user_1, long_denial_reason):
    reason_data = {
        'description': long_denial_reason
    }

    perform_failed_create_reason(client, valid_user_1, reason_data)


def perform_repeated_reason(client, url_name, url_args, user, reason_data, existing_reason, initial_count=1):
    assert reason_data['description'].lower(
    ) == existing_reason.description.lower()
    assert user.post_denial_reasons.count() == initial_count
    url = reverse(url_name, kwargs=url_args)
    response = client.post(url, reason_data)
    assert response.status_code == 302
    assert response.url == url
    assert user.post_denial_reasons.count() == initial_count


@pytest.mark.django_db
def test_create_repeated_reason(client, valid_user_1, valid_denial_reason_1, repeated_denial_reason):
    user = create_moderator_test_user(valid_user_1)
    client.force_login(user)
    reason = PostDenialReason(
        description=valid_denial_reason_1, moderator=user)
    reason.save()
    reason_data = {
        'description': repeated_denial_reason
    }

    perform_repeated_reason(
        client, 'moderation:denial-reason-create', {}, user, reason_data, reason)


@pytest.mark.django_db
def test_create_repeated_generic_reason(client, valid_user_1, valid_denial_reason_1, repeated_denial_reason):
    user = create_moderator_test_user(valid_user_1)
    client.force_login(user)
    reason = PostDenialReason(description=valid_denial_reason_1)
    reason.save()
    reason_data = {
        'description': repeated_denial_reason
    }

    perform_repeated_reason(
        client, 'moderation:denial-reason-create', {}, user, reason_data, reason, 0)


def perform_successful_edit_reason(client, user_data, reason_description, reason_data):
    user = create_moderator_test_user(user_data)
    client.force_login(user)
    reason = PostDenialReason(description=reason_description, moderator=user)
    reason.save()
    assert user.post_denial_reasons.count() == 1
    assert user.post_denial_reasons.first() == reason
    url = reverse('moderation:denial-reason-edit', kwargs={'id': reason.id})
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed('moderation/denial_reason_create.html')
    response = client.post(url, reason_data)
    assert response.status_code == 302
    assert response.url == reverse('moderation:denial-reason-list')
    assert user.post_denial_reasons.count() == 1
    assert user.post_denial_reasons.first(
    ).description == reason_data['description']


@pytest.mark.django_db
def test_successful_edit_reason(client, valid_user_1, valid_denial_reason_1, valid_denial_reason_2):
    reason_data = {
        'description': valid_denial_reason_2
    }

    perform_successful_edit_reason(
        client, valid_user_1, valid_denial_reason_1, reason_data)


@pytest.mark.django_db
def test_repeated_same_reason(client, valid_user_1, valid_denial_reason_1, repeated_denial_reason):
    reason_data = {
        'description': repeated_denial_reason
    }

    perform_successful_edit_reason(
        client, valid_user_1, valid_denial_reason_1, reason_data)


@pytest.mark.django_db
def test_successful_edit_reason_another_user(client, valid_user_1, valid_user_2,
                                             valid_denial_reason_1, valid_denial_reason_2):
    user = create_moderator_test_user(valid_user_2)
    reason = PostDenialReason(
        description=valid_denial_reason_2, moderator=user)
    reason.save()
    assert user.post_denial_reasons.count() == 1
    assert user.post_denial_reasons.first() == reason
    reason_data = {
        'description': valid_denial_reason_2
    }

    perform_successful_edit_reason(
        client, valid_user_1, valid_denial_reason_1, reason_data)


def perform_failed_edit_reason(client, user_data, reason_description, reason_data):
    user = create_moderator_test_user(user_data)
    client.force_login(user)
    reason = PostDenialReason(description=reason_description, moderator=user)
    reason.save()
    assert user.post_denial_reasons.count() == 1
    assert user.post_denial_reasons.first() == reason
    url = reverse('moderation:denial-reason-edit', kwargs={'id': reason.id})
    response = client.post(url, reason_data)
    assert response.status_code == 302
    assert response.url == url
    assert user.post_denial_reasons.count() == 1
    assert user.post_denial_reasons.first().description == reason_description


@pytest.mark.django_db
def test_edit_reason_missing_description(client, valid_user_1, valid_denial_reason_1):
    perform_failed_edit_reason(client, valid_user_1, valid_denial_reason_1, {})


@pytest.mark.django_db
def test_edit_reason_short_description(client, valid_user_1, valid_denial_reason_1, short_denial_reason):
    reason_data = {
        'description': short_denial_reason
    }

    perform_failed_edit_reason(
        client, valid_user_1, valid_denial_reason_1, reason_data)


@pytest.mark.django_db
def test_edit_reason_long_description(client, valid_user_1, valid_denial_reason_1, long_denial_reason):
    reason_data = {
        'description': long_denial_reason
    }

    perform_failed_edit_reason(
        client, valid_user_1, valid_denial_reason_1, reason_data)


@pytest.mark.django_db
def test_edit_repeated_reason(client, valid_user_1, valid_denial_reason_1,
                              valid_denial_reason_2, repeated_denial_reason):
    user = create_moderator_test_user(valid_user_1)
    client.force_login(user)
    reason1 = PostDenialReason(
        description=valid_denial_reason_1, moderator=user)
    reason1.save()
    reason2 = PostDenialReason(
        description=valid_denial_reason_2, moderator=user)
    reason2.save()
    reason_data = {
        'description': repeated_denial_reason
    }

    perform_repeated_reason(client, 'moderation:denial-reason-edit',
                            {'id': reason2.id}, user, reason_data, reason1, 2)


@pytest.mark.django_db
def test_edit_repeated_generic_reason(client, valid_user_1, valid_denial_reason_1,
                                      valid_denial_reason_2, repeated_denial_reason):
    user = create_moderator_test_user(valid_user_1)
    client.force_login(user)
    reason1 = PostDenialReason(description=valid_denial_reason_1)
    reason1.save()
    reason2 = PostDenialReason(
        description=valid_denial_reason_2, moderator=user)
    reason2.save()
    reason_data = {
        'description': repeated_denial_reason
    }

    perform_repeated_reason(client, 'moderation:denial-reason-edit',
                            {'id': reason2.id}, user, reason_data, reason1)


@pytest.mark.django_db
def test_edit_reason_another_user(client, valid_user_1, valid_user_2):
    perform_modify_reason_another_user(
        client, 'moderation:denial-reason-edit', valid_user_1, valid_user_2)


@pytest.mark.django_db
def test_edit_reason_no_user(client, valid_user_1):
    perform_modify_reason_no_user(
        client, 'moderation:denial-reason-edit', valid_user_1)
