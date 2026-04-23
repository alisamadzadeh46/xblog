from django.urls import path
from .views import LiveAnalyzeView
app_name = 'seo'
urlpatterns = [
    path('live/', LiveAnalyzeView.as_view(), name='live'),
]
