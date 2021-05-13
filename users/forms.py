from django import forms
from django.conf import settings
from django.contrib.auth import password_validation, authenticate, get_user_model
from django.contrib.auth.models import Group
from django.contrib.admin import widgets
from django.core.exceptions import ValidationError
from django.utils import timezone
from emails.models import create_change_email_confirmation
from .models import validate_user

UserModel = get_user_model()


class RegisterForm(forms.ModelForm):
    password = forms.CharField(label='Password', strip=False, widget=forms.PasswordInput(
        attrs={'autocomplete': 'new-password'}))

    class Meta:
        model = UserModel
        fields = ['username', 'email']

    def _post_clean(self):
        super()._post_clean()
        password = self.cleaned_data.get('password')

        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as err:
                self.add_error('password', err)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

        return user


class AdminRegisterForm(RegisterForm):
    date_activated_at = forms.DateTimeField(
        required=False, widget=widgets.AdminDateWidget())
    time_activated_at = forms.DateTimeField(
        required=False, widget=widgets.AdminTimeWidget())
    activated_at = forms.SplitDateTimeField(
        required=False, widget=widgets.AdminSplitDateTime)


class DeleteAccountForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['delete_requested_at']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.delete_requested_at = timezone.now()

        if commit:
            user.save()

        return user


class CancelDeleteAccountForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['delete_requested_at']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.delete_requested_at = None

        if commit:
            user.save()

        return user


class AccountForm(forms.ModelForm):
    new_email = forms.EmailField(required=False, label='Email', widget=forms.EmailInput(
        attrs={'autocomplete': 'email'}))
    profile_pic = forms.ImageField(
        required=False, label='Profile Picture', widget=forms.FileInput)
    current_password = forms.CharField(required=False, label='Current Password',
                                       strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    new_password = forms.CharField(required=False, label='New Password', strip=False,
                                   widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))

    class Meta:
        model = UserModel
        fields = ['profile_pic']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_email'].initial = self.instance.email
        self.email_changed = False

    def _post_clean(self):
        super()._post_clean()
        current_password = self.cleaned_data.get('current_password')
        new_password = self.cleaned_data.get('new_password')
        new_email = self.cleaned_data.get('new_email')

        if new_password:
            try:
                password_validation.validate_password(
                    new_password, self.instance)
            except ValidationError as err:
                self.add_error('new_password', err)

            if not current_password:
                self.add_error('current_password', 'This field is required.')

            if self.instance.check_password(new_password):
                self.add_error(
                    'new_password', 'New password cannot be the same as the current one.')

            if new_email:
                try:
                    user_tmp = UserModel(email=new_email)
                    password_validation.validate_password(
                        new_password, user_tmp)
                except ValidationError as err:
                    self.add_error('new_password', err)

        if current_password and not self.instance.check_password(current_password):
            self.add_error('current_password', 'Incorrect password.')

    def clean_new_email(self):
        new_email = self.cleaned_data.get('new_email')

        if new_email:
            user = UserModel.objects.filter(email=new_email).first()

            if user and user != self.instance:
                raise ValidationError('User with this Email already exists.')

        return new_email

    def clean_profile_pic(self):
        profile_pic = self.cleaned_data.get('profile_pic')

        if profile_pic and profile_pic != self.instance.DEFAULT_PROFILE_PIC:
            ext = profile_pic.name.split('.')[-1]

            if ext.lower() not in settings.VALID_PROFILE_PIC_FILETYPES:
                formats = ', '.join(settings.VALID_PROFILE_PIC_FILETYPES)
                raise ValidationError(
                    f'File does not have an approved format: {formats}')

        return profile_pic

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data['new_password']

        if new_password:
            user.set_password(new_password)

        if commit:
            user.save()
            self.email_changed = create_change_email_confirmation(
                user, self.cleaned_data['new_email'])

        return user


class AdminAccountForm(AccountForm):
    date_activated_at = forms.DateTimeField(
        required=False, widget=widgets.AdminDateWidget())
    time_activated_at = forms.DateTimeField(
        required=False, widget=widgets.AdminTimeWidget())
    activated_at = forms.SplitDateTimeField(
        required=False, widget=widgets.AdminSplitDateTime)
    groups = forms.ModelMultipleChoiceField(
        required=False, widget=forms.CheckboxSelectMultiple, queryset=Group.objects.all())


class LoginForm(forms.Form):
    username = forms.CharField(label='Email or Username')
    password = forms.CharField(label='Password', strip=False, widget=forms.PasswordInput(
        attrs={'autocomplete': 'new-password'}))

    def __init__(self, *args, **kwargs):
        self.user_cache = None
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        self.user_cache = None

        if username and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password)

            messages = {
                'user_not_found': 'User not found. Please check if the informed data is correct.'
            }

            validate_user(self.user_cache, ValidationError, messages)

        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class ResetPasswordForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(
        attrs={'autocomplete': 'email'}))

    def __init__(self, *args, **kwargs):
        self.user_cache = None
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        email = self.cleaned_data.get('email')
        self.user_cache = None

        if email:
            self.user_cache = UserModel.objects.filter(email=email).first()

            messages = {
                'user_not_found': 'User not found. Please check if the informed data is correct.'
            }

            validate_user(self.user_cache, ValidationError, messages)

        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class ResetPasswordTokenForm(forms.Form):
    password = forms.CharField(label='New Password', strip=False, widget=forms.PasswordInput(
        attrs={'autocomplete': 'new-password'}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if password:
            password_validation.validate_password(password, self.user)

            if self.user.check_password(password):
                raise ValidationError(
                    'New password cannot be the same as the current one.')

        return password

    def save(self, commit=True):
        password = self.cleaned_data['password']
        self.user.set_password(password)

        if commit:
            self.user.save()

        return self.user
