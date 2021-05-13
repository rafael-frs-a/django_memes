from django.urls import path
from . import views

app_name = 'posts'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('post/', views.CreatePostView.as_view(), name='create-post'),
    path('my-posts/', views.UserPostsView.as_view(), name='user-posts'),
    path('post/<str:id>/', views.PostView.as_view(), name='post-view'),
    path('author/<str:username>/', views.AuthorPostsView.as_view(), name='author-posts'),
]
