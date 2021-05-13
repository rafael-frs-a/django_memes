from django.urls import path
from . import views

app_name = 'moderation'
urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('denial-reasons/', views.ReasonsListView.as_view(),
         name='denial-reason-list'),
    path('denial-reasons/delete/<int:id>/',
         views.ReasonDeleveView.as_view(), name='denial-reason-delete'),
    path('denial-reasons/create/', views.ReasonCreateView.as_view(),
         name='denial-reason-create'),
    path('denial-reasons/edit/<int:id>/',
         views.ReasonUpdateView.as_view(), name='denial-reason-edit'),
    path('moderate/', views.ModerateStartView.as_view(), name='moderate-start'),
    path('moderate/fetch/', views.ModerateFetchView.as_view(), name='moderate-fetch'),
    path('moderate/stop/', views.StopModerateView.as_view(), name='moderate-stop'),
    path('moderate/post/<str:id>/',
         views.ModeratePostView.as_view(), name='moderate-post'),
    path('moderate/post/<str:id>/approve/',
         views.ModerateApproveView.as_view(), name='moderate-approve'),
    path('moderate/post/<str:id>/deny/',
         views.ModerateDenyView.as_view(), name='moderate-deny'),
]
