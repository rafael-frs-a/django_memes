import os
from random import randint
from django.db import models
from django.db.models.signals import post_save, pre_save, pre_delete
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, Group
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinLengthValidator, MaxValueValidator
from django.core.files.storage import default_storage
from django.utils.crypto import salted_hmac


class UserManager(BaseUserManager):
    def add_group(self, user, group_name):
        group = Group.objects.filter(name=group_name).first()

        if not group:
            group = Group(name=group_name)
            group.save()

        user.groups.add(group)
        user.save()

    def create_user(self, username, email, password=None, is_active=False, is_staff=False,
                    is_moderator=False, is_banned=False, banned_seconds=0):
        if not username:
            raise ValueError('Field username required')

        if not email:
            raise ValueError('Field email required')

        if not password:
            raise ValueError('Field password required')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)

        if is_active:
            user.activated_at = timezone.now()

        user.banned = is_banned

        if banned_seconds:
            user.banned_until = timezone.now() + timezone.timedelta(seconds=banned_seconds)

        user.save()

        if is_staff:
            self.add_group(user, 'admin')

        if is_moderator:
            self.add_group(user, 'moderator')

        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(
            username, email, password=password, is_active=True, is_staff=True)
        return user

    def _replace_kwargs(self, kwargs):
        if 'username' in kwargs:
            kwargs['username__iexact'] = kwargs['username']
            del kwargs['username']

        if 'email' in kwargs:
            kwargs['email__iexact'] = kwargs['email']
            del kwargs['email']

    def filter(self, **kwargs):
        self._replace_kwargs(kwargs)
        return super().filter(**kwargs)


def _profile_pic_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    return f'{User.PROFILE_PICS_FOLDER}/{instance.username}{ext}'


class User(AbstractBaseUser):
    DEFAULT_PROFILE_PIC = 'default_profile_pic.jpg'
    PROFILE_PICS_FOLDER = 'profile_pics'

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=20, unique=True, validators=[
                                UnicodeUsernameValidator(), MinLengthValidator(4)])
    profile_pic = models.ImageField(
        default=DEFAULT_PROFILE_PIC, upload_to=_profile_pic_path)
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(blank=True, null=True)
    banned = models.BooleanField(default=False)
    banned_until = models.DateTimeField(blank=True, null=True)
    temporary_bans = models.PositiveSmallIntegerField(default=0)
    groups = models.ManyToManyField(Group, through='GroupUser')
    login_id = models.BigIntegerField(unique=True)
    max_posts_interval = models.PositiveSmallIntegerField(
        default=settings.MIN_MAX_CONSECUTIVE_POSTS, validators=[MaxValueValidator(settings.MAX_MAX_CONSECUTIVE_POSTS)])
    count_posts_interval = models.PositiveSmallIntegerField(default=0)
    post_wait_until = models.DateTimeField(blank=True, null=True)
    delete_requested_at = models.DateTimeField(blank=True, null=True)
    deleted = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def get_rand_id(self):
        user_count = User.objects.count()

        while True:
            rand_id = randint(1, int(1e10) + user_count)

            if not User.objects.filter(login_id=rand_id).first():
                return rand_id

    def save(self, *args, **kwargs):
        if not self.login_id:
            self.login_id = self.get_rand_id()

        super().save(*args, **kwargs)

    def increase_post_count(self):
        last_post = self.posts.order_by('-created_at').first()

        if last_post and last_post.created_at + timezone.timedelta(seconds=settings.POST_WAITING_INTERVAL) <= timezone.now():
            self.count_posts_interval = 0

        self.count_posts_interval += 1

        if self.count_posts_interval >= self.max_posts_interval:
            self.post_wait_until = timezone.now() + \
                timezone.timedelta(seconds=settings.POST_WAITING_INTERVAL)
            self.count_posts_interval = 0

    def has_group(self, group):
        return self.groups.filter(name=group).exists()

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def get_session_auth_hash(self):
        key_salt = settings.SECRET_KEY

        return salted_hmac(
            key_salt,
            f'{self.login_id}',
            algorithm='sha256',
        ).hexdigest()

    @property
    def is_staff(self):
        return self.has_group('admin')

    @property
    def is_moderator(self):
        return self.has_group('moderator')

    @property
    def is_active(self):
        return self.activated_at is not None

    @property
    def group_names(self):
        names = [group.name for group in self.groups.order_by('name')]
        return ', '.join(names)

    @property
    def post_count(self):
        return self.posts.count()

    @property
    def approved_posts(self):
        from posts.models import Post
        return self.posts.filter(moderation_status=Post.APPROVED)


class GroupUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'group')


def validate_user(user, exception_class=ValueError, exception_messages={}):
    if not user:
        msg = exception_messages.get('user_not_found', 'User not found.')
        raise exception_class(msg)

    if not user.is_active:
        msg = exception_messages.get(
            'user_not_activated', 'User not activated yet.')
        raise exception_class(msg)

    if user.banned:
        msg = exception_messages.get(
            'user_banned', 'User banned indefinitely.')
        raise exception_class(msg)

    if user.banned_until and user.banned_until > timezone.now():
        diff = int((user.banned_until - timezone.now()).total_seconds())
        hours = diff // (60 * 60)
        minutes = (diff % (60 * 60)) // 60
        seconds = diff % (60 * 60) % 60
        msg = exception_messages.get(
            'user_banned_until', 'User temporarily banned. Ban time remaining: {:02d}:{:02d}:{:02d}.')
        raise exception_class(msg.format(hours, minutes, seconds))

    if user.deleted:
        msg = exception_messages.get('user_deleted', 'User deleted.')
        raise exception_class(msg)


def get_user_from_token(token, url_name, max_age, validate=True):
    from emails.models import get_email_from_token

    email = get_email_from_token(token, url_name, max_age)
    user = User.objects.filter(email=email).first()

    if validate:
        validate_user(user)

    return user


def __create_activation_email(sender, instance, created, **kwargs):
    if not created:
        return

    from emails.models import create_activation_email
    create_activation_email(instance)


def delete_user_profile_pic(user):
    if user.profile_pic == User.DEFAULT_PROFILE_PIC:
        return

    if default_storage.exists(user.profile_pic.name):
        default_storage.delete(user.profile_pic.name)


def cancel_delete_account(current_user, token):
    user = get_user_from_token(
        token, 'cancel-delete-account', settings.ACCOUNT_DELETION_INTERVAL, validate=False)

    if not user:
        raise ValueError('User not found.')

    if current_user.is_authenticated and current_user != user:
        raise ValueError('User not recognized.')

    if not user.delete_requested_at:
        raise ValueError('Account deletion not requested.')

    user.delete_requested_at = None
    user.save()


def __delete_old_profile_pic_pre_save(sender, instance, **kwargs):
    current_user = User.objects.filter(id=instance.id).first()

    if not current_user or instance.profile_pic == current_user.profile_pic:
        return

    delete_user_profile_pic(current_user)


def __delete_old_profile_pic_pre_delete(sender, instance, **kwargs):
    current_user = User.objects.filter(id=instance.id).first()

    if not current_user:
        return

    delete_user_profile_pic(current_user)


def __logout_banned_user(sender, instance, **kwargs):
    if instance.banned or (instance.banned_until and instance.banned_until > timezone.now()):
        instance.login_id = instance.get_rand_id()


def __delete_account(sender, instance, **kwargs):
    from emails.models import create_delete_account_email
    current_user = User.objects.filter(id=instance.id).first()

    if current_user and not current_user.delete_requested_at and instance.delete_requested_at:
        create_delete_account_email(instance)


def activate_user(token):
    user = get_user_from_token(
        token, 'account-activation', settings.ACCOUNT_ACTIVATION_EXPIRATION_TIME, False)

    if not user:
        raise ValueError('User not found.')

    if user.activated_at:
        raise ValueError('User already activated.')

    user.activated_at = timezone.now()
    user.save()


def change_user_email(current_user, current_email_token, new_email_token):
    from emails.models import get_email_from_token

    user = get_user_from_token(
        current_email_token, 'change-email', settings.CHANGE_EMAIL_EXPIRATION_TIME)

    if user != current_user:
        raise ValueError('User not recognized.')

    new_email = get_email_from_token(
        new_email_token, 'change-email', settings.CHANGE_EMAIL_EXPIRATION_TIME)

    user = User.objects.filter(email=new_email).first()

    if user:
        raise ValueError('New email already taken.')

    current_user.email = new_email
    current_user.save()


def get_not_activated_users_expired_links():
    now = timezone.now()
    users = User.objects.filter(activated_at=None).order_by('created_at')
    expired_users = []

    for user in users:
        if user.created_at + timezone.timedelta(seconds=settings.ACCOUNT_ACTIVATION_EXPIRATION_TIME) <= now:
            expired_users.append(user)

    return expired_users


def get_users_execute_delete_request():
    now = timezone.now()
    users = User.objects.filter(
        delete_requested_at__isnull=False, deleted=False).order_by('delete_requested_at')
    delete_request_users = []

    for user in users:
        if user.delete_requested_at + timezone.timedelta(seconds=settings.ACCOUNT_DELETION_INTERVAL) <= now:
            delete_request_users.append(user)

    return delete_request_users


def execute_user_delete_request(user):
    user.posts.all().delete()
    user.emails.all().delete()
    user.profile_pic = user.DEFAULT_PROFILE_PIC
    delete_user_profile_pic(user)
    user.login_id = user.get_rand_id()
    user.email = f'deleted.user.{user.id}@djangomemes.com'
    user.deleted = True
    user.save()


post_save.connect(__create_activation_email, sender=User)
pre_save.connect(__delete_old_profile_pic_pre_save, sender=User)
pre_save.connect(__logout_banned_user, sender=User)
pre_delete.connect(__delete_old_profile_pic_pre_delete, sender=User)
pre_save.connect(__delete_account, sender=User)
