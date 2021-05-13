from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


def logout_required(func):
    @wraps(func)
    def _wrapped(request, *args, **kwargs):
        user = getattr(request, 'user', None)

        if user and user.is_authenticated:
            messages.warning(request,
                             'This action cannot be completed while you are logged in. Please, logout first.')
            return redirect('posts:home')

        return func(request, *args, **kwargs)

    return _wrapped


def handle_admin_redirect(func):
    @wraps(func)
    def _wrapped(request, *args, **kwargs):
        user = getattr(request, 'user', None)
        next_url = request.GET.get('next')

        if user and user.is_authenticated and not user.is_staff and next_url and next_url.startswith('/admin/'):
            raise PermissionDenied()

        return func(request, *args, **kwargs)

    return _wrapped
