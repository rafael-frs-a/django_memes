from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Post


class CreatePostForm(forms.ModelForm):
    meme_file = forms.ImageField(label='Load Meme', widget=forms.FileInput)

    class Meta:
        model = Post
        fields = ['meme_file']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.author = user

    def clean_meme_file(self):
        meme_file = self.cleaned_data.get('meme_file')

        if meme_file:
            ext = meme_file.name.split('.')[-1]

            if ext.lower() not in settings.VALID_MEME_FILETYPES:
                formats = ', '.join(settings.VALID_MEME_FILETYPES)
                raise ValidationError(
                    f'Files does not have an approved format : {formats}')

        return meme_file

    def clean(self):
        super().clean()

        if self.instance.author.post_wait_until and self.instance.author.post_wait_until > timezone.now():
            diff = self.instance.author.post_wait_until - timezone.now()
            diff = int(diff.total_seconds())
            hours = diff // (60 * 60)
            minutes = (diff % (60 * 60)) // 60
            seconds = diff % (60 * 60) % 60
            msg = f'Max number of {self.instance.author.max_posts_interval} posts reached. ' + \
                'Time remaining until you can post again: {:02d}:{:02d}:{:02d}.'
            raise ValidationError(msg.format(hours, minutes, seconds))

        return self.cleaned_data
