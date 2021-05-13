from django.shortcuts import redirect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from base.views import perform_prg, load_timed_token
from emails.models import create_reset_password_email
from .decorators import logout_required, handle_admin_redirect
from .forms import (RegisterForm, LoginForm, ResetPasswordForm, ResetPasswordTokenForm,
                    AccountForm, DeleteAccountForm, CancelDeleteAccountForm)
from .models import activate_user, get_user_from_token, change_user_email, cancel_delete_account


@require_http_methods(['GET', 'POST'])
@logout_required
def register(request):
    def register_is_valid(request, form):
        form.save()
        messages.success(
            request, 'An activation mail was sent to you. Please activate your account before login.')
        return redirect('users:login')

    return perform_prg(request, RegisterForm, {}, 'users/register.html',
                       {'title': 'Sign Up'}, register_is_valid)


@require_http_methods(['GET', 'POST'])
@handle_admin_redirect
@logout_required
def login(request):
    def login_is_valid(request, form):
        auth_login(request, form.get_user())
        url = request.GET.get('next', 'posts:home')

        if url == reverse('users:logout'):
            url = 'posts:home'

        return redirect(url)

    return perform_prg(request, LoginForm, {}, 'users/login.html',
                       {'title': 'Log In'}, login_is_valid)


@require_http_methods(['GET', 'POST'])
@login_required
def logout(request):
    auth_logout(request)
    return redirect('posts:home')


@require_http_methods(['GET', 'POST'])
@logout_required
def activate_account(request, token):
    def activate_user_():
        activate_user(token)

    if load_timed_token(request, activate_user_):
        messages.success(request, 'Account activated.')

    return redirect('users:login')


@require_http_methods(['GET', 'POST'])
@logout_required
def reset_password(request):
    def reset_password_is_valid(request, form):
        create_reset_password_email(form.get_user())
        messages.success(request, 'A recovery mail was sent to you.')
        return redirect('users:login')

    context = {
        'title': 'Reset Password',
        'btn_title': 'Send Recovery Email'
    }

    return perform_prg(request, ResetPasswordForm, {}, 'users/reset_password.html',
                       context, reset_password_is_valid)


@require_http_methods(['GET', 'POST'])
@logout_required
def reset_password_token(request, token):
    def get_user_from_token_():
        request.session['user-reset-password'] = get_user_from_token(
            token, 'reset-password', settings.RESET_PASSWORD_EXPIRATION_TIME)

    if not load_timed_token(request, get_user_from_token_):
        return redirect('users:login')

    def reset_password_token_is_valid(request, form):
        form.save()
        messages.success(request, 'Password successfully reset.')
        return redirect('users:login')

    user = request.session.pop('user-reset-password')
    return perform_prg(request, ResetPasswordTokenForm, {'user': user},
                       'users/reset_password_token.html', {'title': 'Reset Password'}, reset_password_token_is_valid)


@require_http_methods(['GET', 'POST'])
@login_required
def account(request):
    def account_is_valid(request, form):
        form.save()
        messages.success(request, 'Changes saved.')

        if form.email_changed:
            messages.info(
                request, 'A confirmation mail has been sent to the new email address. Your email address will only change after confirmation.')

        return redirect('posts:home')

    return perform_prg(request, AccountForm, {'instance': request.user}, 'users/account.html',
                       {'title': 'Account'}, account_is_valid)


@require_http_methods(['GET', 'POST'])
@login_required
def change_email(request, current_email_token, new_email_token):
    def change_user_email_():
        change_user_email(request.user, current_email_token, new_email_token)

    if load_timed_token(request, change_user_email_):
        messages.success(request, 'Email changed successfully.')

    return redirect('users:account')


@require_http_methods(['GET', 'POST'])
@login_required
def delete_account(request):
    if request.user.delete_requested_at:
        messages.error(request, 'Account deletion already requested.')
        return redirect('users:account')

    def delete_is_valid(request, form):
        form.save()
        messages.success(request,
                         'Account deletion requested successfully. A detailed email was sent to you.')
        return redirect('users:account')

    context_data = {
        'title': 'Delete Account',
        'hours': settings.ACCOUNT_DELETION_INTERVAL // 60 // 60
    }

    return perform_prg(request, DeleteAccountForm, {'instance': request.user},
                       'users/delete_account.html', context_data, delete_is_valid)


@require_http_methods(['GET', 'POST'])
@login_required
def cancel_delete_account_view(request):
    if not request.user.delete_requested_at:
        messages.error(request, 'Account deletion not requested.')
        return redirect('users:account')

    def cancel_is_valid(request, form):
        form.save()
        messages.success(request, 'Account deletion cancelled successfully.')
        return redirect('users:account')

    return perform_prg(request, CancelDeleteAccountForm, {'instance': request.user},
                       'users/cancel_delete_account.html', {'title': 'Cancel Account Deletion'}, cancel_is_valid)


@require_http_methods(['GET', 'POST'])
def cancel_delete_account_token(request, token):
    def cancel_delete_account_():
        cancel_delete_account(request.user, token)

    if load_timed_token(request, cancel_delete_account_):
        messages.success(request, 'Account deletion cancelled successfully.')

    if request.user.is_authenticated:
        return redirect('users:account')

    return redirect('posts:home')
