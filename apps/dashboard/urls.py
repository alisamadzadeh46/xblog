from django.urls import path
from . import views
app_name = 'dashboard'
urlpatterns = [
    path('',                              views.HomeView.as_view(),           name='home'),
    path('posts/',                        views.PostListView.as_view(),       name='posts'),
    path('posts/new/',                    views.PostCreateView.as_view(),     name='post_create'),
    path('posts/<slug:slug>/edit/',       views.PostEditView.as_view(),       name='post_edit'),
    path('posts/<slug:slug>/delete/',     views.PostDeleteView.as_view(),     name='post_delete'),
    path('posts/<slug:slug>/status/',     views.PostStatusView.as_view(),     name='post_status'),
    path('categories/',                   views.CategoryListView.as_view(),   name='categories'),
    path('categories/new/',               views.CategoryCreateView.as_view(), name='cat_create'),
    path('categories/<int:pk>/edit/',     views.CategoryEditView.as_view(),   name='cat_edit'),
    path('categories/<int:pk>/delete/',   views.CategoryDeleteView.as_view(), name='cat_delete'),
    path('comments/',                     views.CommentListView.as_view(),    name='comments'),
    path('comments/<int:pk>/action/',     views.CommentActionView.as_view(),  name='comment_action'),
    path('analytics/',                    views.AnalyticsView.as_view(),      name='analytics'),
    path('newsletter/',                   views.NewsletterView.as_view(),     name='newsletter'),
    path('users/',                        views.UserListView.as_view(),       name='users'),
    path('users/<int:pk>/toggle/',        views.UserToggleView.as_view(),     name='user_toggle'),
    path('settings/',                     views.SettingsView.as_view(),       name='settings'),
]
