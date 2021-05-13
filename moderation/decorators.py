from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required


def moderator_required(func):
    @wraps(func)
    def _wrapped(request, *args, **kwargs):
        user = getattr(request, 'user', None)

        if user and not user.is_moderator:
            raise PermissionDenied()

        return func(request, *args, **kwargs)

    return login_required(_wrapped)
