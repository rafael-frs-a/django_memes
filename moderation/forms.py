from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from .models import ModerationStatus, get_denial_reasons_moderator, ban_post_denied_author


class DenyPostForm(forms.ModelForm):
    ban_user = forms.BooleanField(required=False,
                                  label=f'Ban user for {settings.USER_TEMPORARY_BAN // 60 // 60} hours')

    class Meta:
        model = ModerationStatus
        fields = ['denial_reason', 'denial_detail']
        widgets = {
            'denial_detail': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }

    def __init__(self, user, post, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.moderator_result = user
        self.instance.post = post
        self.instance.result = ModerationStatus.DENIED
        self.fields['denial_reason'].required = True
        self.fields['denial_reason'].queryset = get_denial_reasons_moderator(
            user)

    def clean_ban_user(self):
        ban_user = self.cleaned_data.get('ban_user')

        if ban_user:
            if self.instance.post.author.is_moderator:
                raise ValidationError('You cannot ban another moderator.')

            if self.instance.post.author.is_staff:
                raise ValidationError('You cannot ban an admin.')

        return ban_user

    def save(self, commit=True):
        status = super().save(commit)
        ban_user = self.cleaned_data.get('ban_user')

        if commit and ban_user:
            ban_post_denied_author(status)

        return status
