from django.urls import path
from . import views
app_name = 'blog'
urlpatterns = [
    path('',                            views.HomeView.as_view(),      name='home'),
    path('post/<slug:slug>/',           views.PostDetailView.as_view(),name='post'),
    path('category/<slug:slug>/',       views.CategoryView.as_view(),  name='category'),
    path('tag/<slug:slug>/',            views.TagView.as_view(),       name='tag'),
    path('author/<slug:slug>/',         views.AuthorView.as_view(),    name='author'),
    path('search/',                     views.SearchView.as_view(),    name='search'),
    path('post/<slug:slug>/comment/',   views.CommentView.as_view(),   name='comment'),
    path('post/<slug:slug>/like/',      views.LikeView.as_view(),      name='like'),
    path('subscribe/',                  views.SubscribeView.as_view(), name='subscribe'),
    path('robots.txt',                  views.RobotsView.as_view(),    name='robots'),
]
