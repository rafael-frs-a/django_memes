import pytest
from django.urls import reverse
from .test_utils import create_test_user


@pytest.mark.django_db
@pytest.mark.parametrize('view', [
    ('posts:home', {}, 200, 405, 405, 405, 405),
    ('posts:user-posts', {}, 200, 405, 405, 405, 405),
    ('posts:post-view', {'id': 'id'}, 404, 405, 405, 405, 405),
    ('posts:author-posts', {'username': 'username'}, 404, 405, 405, 405, 405),
])
def test_requests(client, view, valid_user_1):
    user = create_test_user(valid_user_1)
    client.force_login(user)
    url = reverse(view[0], kwargs=view[1])
    response = client.get(url, follow=True)
    assert response.status_code == view[2]
    response = client.post(url, follow=True)
    assert response.status_code == view[3]
    response = client.delete(url, follow=True)
    assert response.status_code == view[4]
    response = client.put(url, follow=True)
    assert response.status_code == view[5]
    response = client.patch(url, follow=True)
    assert response.status_code == view[6]
