from django.conf import settings
from django.http import HttpResponseNotAllowed
from django.template.loader import render_to_string


class HttpResponseNotAllowedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if isinstance(response, HttpResponseNotAllowed):
            context = {
                'APP_NAME': settings.APP_NAME,
                'title': 'Method Not Allowed',
                'user': request.user
            }

            response.content = render_to_string('errors/405.html', context)

        return response
