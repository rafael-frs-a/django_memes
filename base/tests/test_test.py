from django.conf import settings
from pytest_django.asserts import assertTemplateUsed


def test_test_mode():
    assert settings.TEST_MODE


def test_file_storage():
    assert settings.DEFAULT_FILE_STORAGE == 'inmemorystorage.InMemoryStorage'


def test_404(client, invalid_url):
    response = client.get(invalid_url)
    assert response.status_code == 404
    assertTemplateUsed(response, 'errors/404.html')
