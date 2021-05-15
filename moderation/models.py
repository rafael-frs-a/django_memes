from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, post_delete, pre_delete
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.http import Http404
from django.core.validators import MinLengthValidator
from django.utils import timezone
from posts.models import Post
from emails.models import create_ban_alert_email

UserModel = get_user_model()


class PostDenialReason(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=100, validators=[
                                   MinLengthValidator(10)])
    moderator = models.ForeignKey(UserModel, on_delete=models.CASCADE,
                                  related_name='post_denial_reasons', blank=True, null=True)

    class Meta:
        unique_together = ('description', 'moderator')

    def validate_unique(self, exclude=None):
        if PostDenialReason.objects.exclude(id=self.id).filter(description__iexact=self.description,
                                                               moderator__isnull=True).exists():
            raise ValidationError(
                'Post denial reason with this Description and no Moderator already exists.')

        if PostDenialReason.objects.exclude(id=self.id).filter(description__iexact=self.description,
                                                               moderator=self.moderator).exists():
            raise ValidationError(
                'Post denial reason with this Description and Moderator already exists.')

        super().validate_unique(exclude)

    def __str__(self):
        moderator = self.moderator.username if self.moderator else 'All'
        return f'{self.description}. Moderator: {moderator}'


class ModerationStatus(models.Model):
    MODERATING = 'M'
    APPROVED = 'A'
    DENIED = 'D'
    RESULTS = [
        (MODERATING, 'Moderating'),
        (APPROVED, 'Approved'),
        (DENIED, 'Denied')
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='status')
    moderator_moderating = models.OneToOneField(
        UserModel, on_delete=models.SET_NULL, blank=True, null=True, related_name='status_moderating')
    result = models.CharField(
        max_length=2, choices=RESULTS, default=MODERATING)
    moderator_result = models.ForeignKey(
        UserModel, on_delete=models.SET_NULL, blank=True, null=True)
    denial_reason = models.ForeignKey(
        PostDenialReason, on_delete=models.SET_NULL, blank=True, null=True)
    denial_detail = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('post', 'result', 'moderator_result')

    def clean(self):
        if not self.moderator_result:
            raise ValidationError('Moderator result required.')

        if self.result == ModerationStatus.MODERATING:
            if self.moderator_moderating and self.moderator_moderating != self.moderator_result:
                raise ValidationError(
                    'Moderator moderating must be identical to moderator result.')
        elif self.moderator_moderating:
            raise ValidationError(
                'Moderator moderating cannot be informed when result is not Moderating.')

        if self.result == ModerationStatus.DENIED:
            if not self.denial_reason:
                raise ValidationError(
                    'Denial reason must be informed.')
        elif self.denial_reason:
            raise ValidationError(
                'Denial reason cannot be informed when result is not Denied.')

    def validate_unique(self, exclude=None):
        if self.result == ModerationStatus.MODERATING and ModerationStatus.objects.exclude(
                id=self.id).filter(post=self.post, result=ModerationStatus.MODERATING).exists():
            raise ValidationError('Post already in moderation.')

        super().validate_unique(exclude)

    def __str__(self):
        result = self.result

        for option in ModerationStatus.RESULTS:
            if option[0] == result:
                result = option[1]
                break

        return f'Author: {self.post.author.username}. Identifier: {self.post.identifier}. Moderation result: {result}'


def get_reasons_moderator(moderator, ordering):
    field = ordering[1:] if ordering[0] == '-' else ordering

    if not hasattr(PostDenialReason, field):
        raise Http404()

    order = '-' if ordering[0] == '-' else ''

    if field.lower() == 'description':
        return moderator.post_denial_reasons.extra(
            select={'lower': 'lower(description)'}).order_by(f'{order}lower')

    return moderator.post_denial_reasons.order_by(f'{order}{field}')


def get_total_reasons_moderator(moderator):
    return moderator.post_denial_reasons.count()


def get_denial_reason(moderator, id_):
    reason = moderator.post_denial_reasons.filter(id=id_).first()

    if not reason:
        raise Http404()

    return reason


def get_status_moderating(moderator):
    if not moderator:
        return None

    try:
        return moderator.status_moderating
    except ModerationStatus.DoesNotExist:
        return None


def get_post_moderating(moderator):
    status = get_status_moderating(moderator)

    if status:
        return status.post

    return None


def check_post_moderating(moderator, identifier):
    post = get_post_moderating(moderator)

    if not post or post.identifier != identifier:
        raise Http404()

    return post


def fetch_post_moderate(moderator):
    if not moderator.is_moderator:
        return None

    post = get_post_moderating(moderator)

    if post:
        return post

    now = timezone.now()
    post = Post.objects.filter(Q(moderation_status=Post.WAITING_MODERATION), Q(author__banned=False), Q(
        author__banned_until__isnull=True) | Q(author__banned_until__lte=now)).order_by('created_at').first()

    if not post:
        return None

    status = ModerationStatus(
        post=post, moderator_moderating=moderator, moderator_result=moderator)
    status.save()
    return post


def stop_moderating(moderator):
    status = get_status_moderating(moderator)

    if status:
        status.delete()


def approve_post(moderator, identifier):
    check_post_moderating(moderator, identifier)
    post = moderator.status_moderating.post
    status = ModerationStatus(
        post=post, result=ModerationStatus.APPROVED, moderator_result=moderator)
    status.save()


def get_denial_reasons_moderator(moderator):
    return PostDenialReason.objects.filter(
        Q(moderator=moderator) | Q(moderator__isnull=True)).extra(
        select={'lower': 'lower(description)'}).order_by('-moderator', 'lower').all()


def ban_post_denied_author(moderation_status):
    user = moderation_status.post.author

    if user.is_staff or user.is_moderator:
        return

    user.temporary_bans += 1

    if user.temporary_bans >= settings.USER_PERM_BAN_COUNT:
        user.banned = True
    else:
        user.banned_until = timezone.now(
        ) + timezone.timedelta(seconds=settings.USER_TEMPORARY_BAN)

    user.save()
    create_ban_alert_email(moderation_status)


def __change_post_moderation_status(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.result == ModerationStatus.MODERATING:
        instance.post.moderation_status = Post.MODERATING
    elif instance.result == ModerationStatus.DENIED:
        instance.post.moderation_status = Post.DENIED
    elif instance.result == ModerationStatus.APPROVED:
        instance.post.moderation_status = Post.APPROVED
        instance.post.approved_at = timezone.now()

    if instance.post.moderation_status != Post.APPROVED:
        instance.post.approve_post = None
        instance.post.meme_labelled = False
        instance.post.meme_text = None
        instance.post.tags.all().delete()

    instance.post.save()


def __clean_moderator_moderating(sender, instance, created, **kwargs):
    if instance.result in (ModerationStatus.DENIED, ModerationStatus.APPROVED):
        status_moderating = get_status_moderating(instance.moderator_result)

        if status_moderating:
            status_moderating.moderator_moderating = None
            status_moderating.save()


def __change_post_moderation_status_back(sender, instance, **kwargs):
    last_status = instance.post.status.order_by('-created_at').first()

    if not last_status:
        instance.post.moderation_status = Post.WAITING_MODERATION
    elif last_status.result == ModerationStatus.APPROVED:
        instance.post.moderation_status = Post.APPROVED
    elif last_status.result == ModerationStatus.DENIED:
        instance.post.moderation_status = Post.DENIED
    elif last_status.result == ModerationStatus.MODERATING:
        instance.post.moderation_status = Post.MODERATING

    instance.post.save()


def __remove_post_moderating_user_not_moderator(sender, instance, **kwargs):
    if not instance.user.is_moderator:
        stop_moderating(instance.user)


def __remove_post_moderating_user_deleted(sender, instance, **kwargs):
    stop_moderating(instance)


post_save.connect(__change_post_moderation_status, sender=ModerationStatus)
post_save.connect(__clean_moderator_moderating, sender=ModerationStatus)
post_delete.connect(__change_post_moderation_status_back,
                    sender=ModerationStatus)
post_delete.connect(__remove_post_moderating_user_not_moderator,
                    sender=UserModel.groups.through)
pre_delete.connect(__remove_post_moderating_user_deleted, sender=UserModel)
