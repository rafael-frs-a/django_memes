import os
import pytest
from django.core.files import File
from django.core.files.storage import default_storage
from .test_utils import create_test_user, create_test_post


@pytest.mark.django_db
def test_change_post_img(valid_user_1, valid_image_file_1, valid_image_file_2):
    user = create_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file_1)
    old_file = post.meme_file.name
    assert default_storage.exists(old_file)
    current_path = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_path, 'images', valid_image_file_2)
    post.meme_file.save(valid_image_file_2, File(open(image_path, 'rb')))
    post.save()
    assert not default_storage.exists(old_file)
    assert default_storage.exists(post.meme_file.name)


@pytest.mark.django_db
def test_delete_post(valid_user_1, valid_image_file_1):
    user = create_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file_1)
    old_file = post.meme_file.name
    assert default_storage.exists(old_file)
    post.delete()
    assert not default_storage.exists(old_file)
    assert user.posts.count() == 0


@pytest.mark.django_db
def test_delete_post_file_not_found(valid_user_1, valid_image_file_1):
    user = create_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file_1)
    old_file = post.meme_file.name
    assert default_storage.exists(old_file)
    default_storage.delete(old_file)
    assert not default_storage.exists(old_file)
    post.delete()
    assert user.posts.count() == 0


@pytest.mark.django_db
def test_delete_folder(valid_user_1, valid_image_file_1, valid_image_file_2):
    user = create_test_user(valid_user_1)
    post1 = create_test_post(user, valid_image_file_1)
    post2 = create_test_post(user, valid_image_file_2)
    old_file1 = post1.meme_file.name
    old_file2 = post2.meme_file.name
    folder = os.path.dirname(old_file1)
    assert folder == os.path.dirname(old_file2)

    trash = default_storage.listdir(folder)
    old_file1_name = os.path.basename(old_file1)
    old_file2_name = os.path.basename(old_file2)

    for trash_folder in trash[0]:
        folder_delete = os.path.join(folder, trash_folder)
        default_storage.delete(folder_delete)

    for trash_file in trash[1]:
        if trash_file not in (old_file1_name, old_file2_name):
            file_delete = os.path.join(folder, trash_file)
            default_storage.delete(file_delete)

    assert default_storage.exists(old_file1)
    assert default_storage.exists(old_file2)
    assert default_storage.exists(folder)

    post1.delete()
    assert not default_storage.exists(old_file1)
    assert default_storage.exists(old_file2)
    assert default_storage.exists(folder)
    post2.delete()
    assert not default_storage.exists(old_file2)
    assert not default_storage.exists(folder)
