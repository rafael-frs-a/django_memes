import os
import secrets
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, pre_save, post_delete
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.paginator import Paginator
from django.core.files.storage import default_storage
from django.http import Http404
from django.urls import reverse
from django.utils import timezone
from users.models import validate_user
from PIL import Image
from .tasks import get_post_labels

UserModel = get_user_model()


def _meme_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    user_folder = instance.get_user_folder()
    return f'{user_folder}/{instance.identifier}{ext}'


class Post(models.Model):
    MEMES_FOLDER = 'posts'
    WAITING_MODERATION = 'W'
    MODERATING = 'M'
    APPROVED = 'A'
    DENIED = 'D'
    MODERATION_STATUS = [
        (WAITING_MODERATION, 'Waiting for Moderation'),
        (MODERATING, 'Moderating'),
        (APPROVED, 'Approved'),
        (DENIED, 'Denied')
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name='posts')
    meme_file = models.ImageField(upload_to=_meme_path)
    identifier = models.CharField(max_length=40, unique=True)
    moderation_status = models.CharField(
        max_length=2, choices=MODERATION_STATUS, default=WAITING_MODERATION)
    approved_at = models.DateTimeField(blank=True, null=True)
    meme_labels = models.TextField(blank=True, null=True)
    meme_text = models.TextField(blank=True, null=True)
    meme_labelled = models.BooleanField(default=False)

    @property
    def tags_sorted(self):
        return self.tags.order_by('description')

    def get_user_folder(self):
        if not self.author:
            return None

        return f'{Post.MEMES_FOLDER}/{self.author.username}'

    def _get_identifier(self):
        user_folder = self.get_user_folder()

        if not user_folder:
            return None

        while True:
            filename = secrets.token_hex(4)

            if not default_storage.exists(user_folder):
                break

            for file in default_storage.listdir(user_folder)[1]:
                if os.path.splitext(file)[0] == filename:
                    break
            else:
                break

        return filename

    def save(self, *args, **kwargs):
        if not self.identifier:
            self.identifier = self._get_identifier()

        super().save(*args, **kwargs)

        if not settings.TEST_MODE and default_storage.exists(self.meme_file.name):
            img = Image.open(self.meme_file.path)

            if img.height > settings.MEME_SIZE[0] or img.width > settings.MEME_SIZE[1]:
                img.thumbnail(settings.MEME_SIZE)
                img.save(self.meme_file.path)

    def __str__(self):
        status = self.moderation_status

        for option in Post.MODERATION_STATUS:
            if option[0] == status:
                status = option[1]
                break

        return f'Author: {self.author.username}. Post: {self.meme_file.name}. Status: {status}. Labels: {self.meme_labels}'


class PostTag(models.Model):
    description = models.CharField(max_length=100)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='tags')

    class Meta:
        unique_together = ('post', 'description')


def delete_meme_file(post):
    if default_storage.exists(post.meme_file.name):
        default_storage.delete(post.meme_file.name)

    folder = os.path.dirname(post.meme_file.name)

    if default_storage.exists(folder):
        folders, files = default_storage.listdir(folder)

        if not folders and not files:
            default_storage.delete(folder)


def get_approved_posts(page, search_filter, author=None):
    response = {}
    response['posts'] = []
    response['has_next'] = False
    posts = Post.objects.filter(moderation_status=Post.APPROVED)

    if search_filter:
        posts &= Post.objects.filter(Q(meme_labels__search=search_filter) |
                                     Q(meme_text__search=search_filter) |
                                     Q(meme_labels__icontains=search_filter) |
                                     Q(meme_text__icontains=search_filter) |
                                     Q(author__username__icontains=search_filter))

    if author:
        posts &= Post.objects.filter(author=author)

    posts = posts.order_by('-approved_at')
    p = Paginator(posts, settings.POSTS_PER_PAGE)
    page = int(page)

    if page not in p.page_range:
        return response

    response['has_next'] = p.page(page).has_next()
    page_posts = p.page(page).object_list

    for post in page_posts:
        post_data = {}
        post_data['profile_pic_url'] = post.author.profile_pic.url
        post_data['author'] = post.author.username
        post_data['meme_url'] = post.meme_file.url
        post_data['post_link'] = reverse(
            'posts:post-view', kwargs={'id': post.identifier})
        post_data['author_link'] = reverse(
            'posts:author-posts', kwargs={'username': post.author.username})
        post_data['tags'] = [
            _.description for _ in post.tags.order_by('description')]
        response['posts'].append(post_data)

    return response


def get_user_posts(user, page, client_timezone=0):
    from moderation.models import ModerationStatus

    response = {}
    response['posts'] = []
    response['has_next'] = False
    posts = user.posts.order_by('-created_at')
    p = Paginator(posts, settings.POSTS_PER_PAGE)
    page = int(page)
    client_timezone = int(client_timezone)

    if page not in p.page_range:
        return response

    response['has_next'] = p.page(page).has_next()
    page_posts = p.page(page).object_list

    for post in page_posts:
        post_data = {}
        post_data['meme_url'] = post.meme_file.url
        date = post.created_at - timezone.timedelta(minutes=client_timezone)
        date = date.strftime(settings.DATE_TIME_DISPLAY_FORMAT)
        post_data['post_created_at'] = date
        post_data['is_waiting_moderation'] = post.moderation_status == Post.WAITING_MODERATION
        post_data['is_moderating'] = post.moderation_status == Post.MODERATING
        post_data['is_denied'] = post.moderation_status == Post.DENIED
        post_data['is_approved'] = post.moderation_status == Post.APPROVED
        post_data['status_created_at'] = ''
        post_data['denial_reason'] = ''
        post_data['denial_details'] = ''
        status = None

        if post.moderation_status == Post.MODERATING:
            status = post.status.filter(
                result=ModerationStatus.MODERATING).first()
        elif post.moderation_status == Post.DENIED:
            status = post.status.filter(result=ModerationStatus.DENIED).first()
        elif post.moderation_status == Post.APPROVED:
            date = post.approved_at - \
                timezone.timedelta(minutes=client_timezone)
            post_data['status_created_at'] = date.strftime(
                settings.DATE_TIME_DISPLAY_FORMAT)

        if status:
            date = status.created_at - \
                timezone.timedelta(minutes=client_timezone)
            post_data['status_created_at'] = date.strftime(
                settings.DATE_TIME_DISPLAY_FORMAT)

            if post.moderation_status == Post.DENIED:
                post_data['denial_reason'] = status.denial_reason.description
                post_data['denial_details'] = status.denial_detail or 'None'

        response['posts'].append(post_data)

    return response


def get_approved_post(identifier):
    post = Post.objects.filter(
        moderation_status=Post.APPROVED, identifier=identifier).first()

    if not post:
        raise Http404()

    return post


def get_author(username):
    author = UserModel.objects.filter(username=username).first()
    validate_user(author, exception_class=Http404)
    return author


def __delete_old_meme_file_pre_save(sender, instance, **kwargs):
    current_post = Post.objects.filter(id=instance.id).first()

    if not current_post or instance.meme_file == current_post.meme_file:
        return

    delete_meme_file(current_post)


def __delete_old_meme_file(sender, instance, **kwargs):
    delete_meme_file(instance)


def __increase_author_post_count(sender, instance, created, **kwargs):
    if not created:
        return

    instance.author.increase_post_count()
    instance.author.save()


def __get_post_labels(sender, instance, created, **kwargs):
    if settings.TEST_MODE:
        return

    if instance.moderation_status != Post.APPROVED:
        return

    if not instance.meme_labelled:
        get_post_labels.delay(instance.id)


def __label_post(sender, instance, **kwargs):
    labels = [
        _.description for _ in instance.post.tags.order_by('description')]
    instance.post.meme_labels = ' '.join(labels)
    instance.post.save()


pre_save.connect(__delete_old_meme_file_pre_save, sender=Post)
post_delete.connect(__delete_old_meme_file, sender=Post)
post_save.connect(__increase_author_post_count, sender=Post)
post_save.connect(__get_post_labels, sender=Post)
post_save.connect(__label_post, sender=PostTag)
post_delete.connect(__label_post, sender=PostTag)
