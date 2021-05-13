from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('activate-account/<str:token>/',
         views.activate_account, name='activate-account'),
    path('reset-password/', views.reset_password, name='reset-password'),
    path('reset-password/<str:token>/',
         views.reset_password_token, name='reset-password-token'),
    path('account/', views.account, name='account'),
    path('change-email/<str:current_email_token>/<str:new_email_token>/',
         views.change_email, name='change-email'),
    path('account/delete/', views.delete_account, name='delete-account'),
    path('account/delete/cancel/', views.cancel_delete_account_view,
         name='cancel-delete-account'),
    path('account/delete/cancel/<str:token>/',
         views.cancel_delete_account_token, name='cancel-delete-account-token'),
]
