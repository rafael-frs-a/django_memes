from django.urls import path
from . import views

app_name = 'pwa'
urlpatterns = [
    path('sw.js', views.ServiceWorkerView.as_view(), name='sw'),
    path('offline/', views.OfflineView.as_view(), name='offline'),
]
