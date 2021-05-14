from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required
from users import views as user_views

admin.autodiscover()
admin.site.login = login_required(admin.site.login)

urlpatterns = [
    path('admin/logout/', user_views.logout),
    path('admin/login/', RedirectView.as_view(url=settings.LOGIN_URL,
                                              permanent=True, query_string=True)),
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('', include('posts.urls')),
    path('', include('pwa.urls')),
    path('moderation/', include('moderation.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = 'base.views.error_403'
handler404 = 'base.views.error_404'
