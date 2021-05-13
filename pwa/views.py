from django.urls import reverse
from django.templatetags.static import static
from django.views.generic import TemplateView


class ServiceWorkerView(TemplateView):
    template_name = 'pwa/sw.js'
    content_type = 'application/javascript'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['icon_url'] = static('pwa/icons/icon512.png')
        context['offline_url'] = reverse('pwa:offline')
        context['manifest_url'] = static('pwa/manifest.json')
        return context


class OfflineView(TemplateView):
    template_name = 'pwa/offline.html'
